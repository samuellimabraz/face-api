def remove_face_image(data):
    if isinstance(data, dict):
        return {k: remove_face_image(v) for k, v in data.items() if k != 'face_image'}
    elif isinstance(data, list):
        return [remove_face_image(item) for item in data]
    else:
        return data
