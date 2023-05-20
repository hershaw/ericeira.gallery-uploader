import os
import glob
import argparse
import tempfile
from urllib.parse import urlparse
from PIL import Image
import boto3
import threading
from concurrent.futures import ThreadPoolExecutor


def valid_directory(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"{path} is not a valid directory.")
    return path


def valid_s3_url(url):
    parsed_url = urlparse(url)
    if not parsed_url.scheme == "s3" or not parsed_url.netloc or not parsed_url.path:
        raise argparse.ArgumentTypeError(f"{url} is not a valid s3 URL.")
    return url


def create_s3_client(aws_profile_name):
    session = boto3.Session(profile_name=aws_profile_name)
    return session.client("s3")


def upload_image(s3, bucket, key_prefix, output_path, file_name, original_path):

    compressed_s3_path = f"compressed/{key_prefix}/{file_name}"
    with open(output_path, "rb") as output_file:
        s3.upload_fileobj(output_file, bucket, compressed_s3_path)

    original_s3_path = f"original/{key_prefix}/{file_name}"
    with open(original_path, "rb") as original_file:
        s3.upload_fileobj(original_file, bucket, original_s3_path)

    return f"/image https://{bucket}.s3.amazonaws.com/{compressed_s3_path}"


def process_and_upload_images(image_directory, s3, bucket, key_prefix):
    image_paths = glob.glob(os.path.join(image_directory, "*.JPG"))

    with tempfile.TemporaryDirectory() as temp_dir:
        tasks = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            for image_path in image_paths:
                file_name = os.path.basename(image_path)
                output_path = os.path.join(temp_dir, file_name)

                with Image.open(image_path) as img:
                    img.save(output_path, "JPEG", quality=25)

                task = executor.submit(upload_image, s3, bucket, key_prefix, output_path, file_name, image_path)
                tasks.append(task)

            for task in tasks:
                print(task.result())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resize JPEG images and upload to S3")
    parser.add_argument("image_directory", type=valid_directory, help="Path to the image directory")
    parser.add_argument("aws_profile_name", help="AWS profile name for accessing S3")
    parser.add_argument("s3_url", type=valid_s3_url, help="S3 URL in the format s3://bucket/key_prefix")
    args = parser.parse_args()

    parsed_s3_url = urlparse(args.s3_url)
    bucket = parsed_s3_url.netloc
    key_prefix = parsed_s3_url.path.lstrip('/')

    s3 = create_s3_client(args.aws_profile_name)
    process_and_upload_images(args.image_directory, s3, bucket, key_prefix)
