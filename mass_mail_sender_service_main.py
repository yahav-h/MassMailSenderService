if __name__ == '__main__':
    __import__("uvicorn").run('endpoints:app', host="0.0.0.0", port=80)
