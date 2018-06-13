# coding=utf-8

from celery import Celery

from safe.test.qgis_app import qgis_app

# initialize qgis_app
APP, IFACE = qgis_app()

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/11/15'

app = Celery('realtime.tasks')
app.config_from_object('realtime.celeryconfig')

packages = (
    'realtime',
)

app.autodiscover_tasks(packages)

if __name__ == '__main__':
    app.worker_main()
