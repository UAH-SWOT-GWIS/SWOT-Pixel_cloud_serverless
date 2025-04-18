from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

import boto3
import requests

from config import s3BucketName, aws_access_key_id, aws_secret_access_key

s3 = boto3.client("s3",aws_access_key_id=aws_access_key_id, 
                  aws_secret_access_key=aws_secret_access_key)

def upload_stream(download_urls, meta_data,stream_in_chunks = False):
    if not download_urls:
        print(f"No download links found")
        return {
            "status": "failed",
            "message": "No download links found"}
    
    elif stream_in_chunks:
        #implementation needed to download in chunks, if the file_size is large; Need to do it in multipart
        # skipping this implementation as all SWOT data is less than 700MB ~approximately
        print("chunks stream")
        return {
            "status": "failed",
            "message" : "Internal server Error"
        }
    
    s3_dir = f"{meta_data.get('pass', 'unknown')}/{meta_data.get('tile', 'unknown')}/{meta_data.get('date', 'unknown')}/"
    
    print(f"downloading urls {download_urls}")

    res = []

    for url in download_urls:
        file_name = url.split('/')[-1]
        print(f"Downloading {file_name} from {url}")

        # Stream the file directly to S3
        if file_name.endswith('.json'):
            s3_location = s3_dir + 'meta' + '/' + file_name
        else:
            s3_location = s3_dir + file_name
        
        try:
            with fetch_file(url) as response:
                s3.upload_fileobj(response, s3BucketName, s3_location)
            
            print(f"Uploaded {file_name} to s3://{s3BucketName}/{s3_location}")
            res.append({
                "status": "success",
                "pass": meta_data['pass'],
                "tile": meta_data['tile'],
                "message": f"Uploaded {file_name} to s3://{s3BucketName}/{s3_location}"
            })
            

        except Exception as e:
            print(f"Failed to upload {file_name}: {str(e)}")
            res.append({
                "status": "failed",
                "message": f"Error uploading {file_name}: {str(e)}"
            })
    return res

        
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2))
def fetch_file(url):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    return response.raw

def stream_to_s3(granule):
    granule_umm = granule.get('umm', {})
    granule_ur = granule_umm.get('GranuleUR', '')

    info = granule_umm.get('DataGranule', {}).get('ArchiveAndDistributionInformation', [])
    data = [float(x['Size']) for x in info if x.get('Name') == granule_ur + '.nc']
    file_size = data[0] if data else 0.0

    download_urls = granule.data_links()

    granule_track = granule_umm.get('SpatialExtent', {}).get('HorizontalSpatialDomain', {}).get('Track', {}).get('Passes', [])
    pass_no = granule_track[0].get('Pass', 'Unknown') if granule_track else 'Unknown'
    tile = granule_track[0].get('Tiles', ['Unknown'])[0] if granule_track else 'Unknown'
    
    granule_date_range = granule_umm.get('TemporalExtent', {}).get('RangeDateTime', {})
    timestamp = granule_date_range.get('EndingDateTime', '')
    
    date = 'Unknown'
    if timestamp:
        try:
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
            date = dt.date()
        except ValueError:
            pass  # Handle incorrect date format gracefully

    stream_chunks = False  # Enable chunked streaming for large files

    meta_data_urls = granule._filter_related_links("EXTENDED METADATA")
    meta_json_urls = [url for url in meta_data_urls if url.startswith("http") and url.endswith(".json")]
    
    if meta_json_urls:
        download_urls.append(meta_json_urls[0])

    meta_data = {
        "pass": str(pass_no),
        "tile": str(tile),
        "date": str(date),
        "urls": download_urls
    }

    return upload_stream(download_urls, meta_data, stream_chunks)
    