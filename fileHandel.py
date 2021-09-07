

def readfile(file):
    with open(file, "rb") as data:
        return data.readlines()


def write_bytes_to_file(file, text):
    with open(file, "w") as data:
        return data.writelines(text)
