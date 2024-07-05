import oss2
from .oss_conn import establish_connection

def upload_image(image_path, transaction_id):
    auth = establish_connection()

    endpoint = 'oss-cn-beijing.aliyuncs.com'

    bucket = oss2.Bucket(auth, endpoint, 'alpha-record-test')

    bucket.put_object_from_file(f"invest_records/{transaction_id}.jpg", image_path)

def download_image(transaction_id):
    auth = establish_connection()

    endpoint = 'oss-cn-beijing.aliyuncs.com'

    bucket = oss2.Bucket(auth, endpoint, 'alpha-record-test')

    bucket.get_object_to_file(f"invest_records/{transaction_id}.jpg",
                              f"resources/temp/alpha_record/upload/{transaction_id}.jpg")

    return f"resources/temp/alpha_record/upload/{transaction_id}.jpg"