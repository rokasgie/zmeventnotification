import concurrent.futures
import json
import time

import requests

stream = 34
options = {'api': None, 'contig_frames_before_error': 5, 'frame_set': 'snapshot,alarm', 'frame_strategy': 'most_models',
           'max_attempts': 3, 'polygons': [], 'resize': 800, 'sleep_between_attempts': 4}
args = {'bareversion': False, 'config': 'objectconfig.ini', 'debug': False, 'eventid': '34', 'eventpath': '',
        'file': None, 'monitorid': '1', 'notes': False, 'output_path': None, 'reason': None, 'version': False}
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyNDA2NDU1OCwianRpIjoiNjkyNzViYzMtNmEyNi00OWI1LWFkMDMtY2U2OGM5YzllY2NkIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImFkbWluIiwibmJmIjoxNzI0MDY0NTU4LCJjc3JmIjoiNjRlYzQ1ZWYtYjAzNC00NjY2LTg4YmEtN2Y2ZTg2ZDE1MTQ0IiwiZXhwIjoxNzI0MDY4MTU4fQ.jNtkK4NtPbgnuTiBmPaCEsID4xkxGdwKnInOC6fZXUo"
ml_overrides = {'alpr': {'pattern': '.*'}, 'face': {'pattern': '.*'}, 'model_sequence': 'object,face,alpr',
                'object': {'pattern': '(person|car|motorbike|bus|truck|boat)'}}
TOKEN = None


def detect():
    r = requests.post(
        url="http://localhost:5000/api/v1/detect/object?type=object",
        headers={'Authorization': f'Bearer {TOKEN}'},
        params={'delete': True, 'response_format': 'zm_detect'},
        files={},
        json={
            'version': "6.1.29",
            'mid': "1",
            'reason': None,
            'stream': "34",
            'stream_options': options,
            'ml_overrides': ml_overrides
        }
    )
    r.raise_for_status()


def benchmark_detection(max_workers):
    times = []
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_start_time = {executor.submit(detect): time.time() for _ in range(max_workers)}
        for future in concurrent.futures.as_completed(future_to_start_time):
            end_time = time.time()
            start_time_of_task = future_to_start_time[future]
            elapsed_time = end_time - start_time_of_task
            times.append(elapsed_time)

    total_time = time.time() - start_time

    print(f"Total time taken for {max_workers} parallel runs: {total_time:.4f} seconds")
    print(f"Average time taken per instance: {sum(times) / len(times):.4f} seconds")
    print(f"Minimum time taken: {min(times):.4f} seconds")
    print(f"Maximum time taken: {max(times):.4f} seconds")

    return times


if __name__ == "__main__":
    # Try benchmarking with different numbers of workers to find the limit
    r = requests.post(
        url="http://localhost:5000/api/v1/login",
        data=json.dumps({'username': "admin", 'password': "admin"}),
        headers={'content-type': 'application/json'}
    )
    data = r.json()
    TOKEN = data.get('access_token')

    for workers in [1, 2, 4, 8, 16, 32, 64, 128]:
        print(f"\nBenchmarking with {workers} parallel workers:")
        times = benchmark_detection(workers)
