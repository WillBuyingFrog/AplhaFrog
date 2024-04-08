## 启动AlphaFrog

### 1 启动Celery Worker

在`root_of_project/alphafrog`目录下执行：
```shell
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
celery -A alphafrog worker -l info
```


### 2 启动Django Server

在`root_of_project`目录下执行：
```shell
python manage.py runserver 0.0.0.0:8000
```