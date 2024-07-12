from IPDD.celery import app


@app.task(name='test')
def test():
    print('DEBUG: TEST TASK')
