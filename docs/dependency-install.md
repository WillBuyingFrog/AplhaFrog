
## 1 PostgreSQL

### 1.1 安装PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib
```

安装后会输出：
```
Ver Cluster Port Status Owner    Data directory              Log file
12  main    5432 down   postgres /var/lib/postgresql/12/main /var/log/postgresql/postgresql-12-main.log
```

### 1.2 检查PostgreSQL服务状态

```bash
service postgresql status
```

安装PostgreSQL时，系统会自动创建一个名为postgres的默认管理员用户。

登录postgre用户并开始使用psql命令行：

```bash
sudo -u postgres psql
```

### 1.3 允许外部IP访问PostgreSQL

#### 1.3.1 修改postgresql.conf

```bash
sudo vim /etc/postgresql/12/main/postgresql.conf
```

找到`listen_addresses = 'localhost'`，修改为`listen_addresses = '*'`。

#### 1.3.2 修改pg_hba.conf

```bash
sudo vim /etc/postgresql/12/main/pg_hba.conf
```

在文件末尾添加：

```
host    all             all             0.0.0.0/0               md5
```

### 1.3.3 重启服务

```bash
sudo service postgresql restart
```


## 2 Redis

### 2.1 安装Redis

```bash
sudo apt-get install redis
```

### 2.2 检查redis运行状态

```bash
systemctl status redis-server
```


