class DatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'alpharecord':
            print("hi")
            return 'sqlite3'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'alpharecord':
            return 'sqlite3'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'alpharecord' or obj2._meta.app_label == 'alpharecord':
            return 'sqlite3'
        return 'default'

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'alpharecord':
            return db == 'sqlite3'
        return db == 'default'
