import yaml
import os
import chardet
import codecs


class Config:

    _config_file = "TransTools.yaml"
    _config_encoding = "utf-8"
    _config_orm = "orm"
    _orm_default = "default"

    def get_config(self):
        """获取配置文件，并解析为python对象"""
        if not os.path.exists(self._config_file):
            return False, '配置文件{}不存在'.format(self.config_path)
        with open(self._config_file, 'rb') as f:
            encoding = chardet.detect(f.read())['encoding']
        with codecs.open(self._config_file, encoding=encoding) as f:
            try:
                y = yaml.load(f)
            except Exception as e:
                return False, "解析配置文件{}时发生异常:{}".format(self._config_file, str(e))
            return True, y

    def get_orm_engine(self, engine_name=None):
        """获取orm引擎"""
        if engine_name is None:
            engine_name = self._orm_default

        result, config = self.get_config()
        if not result:
            return result, config

        if config.get(self._config_orm, None) is None:
            return False, "配置文件中不存在orm节点"

        orm = config.get(self._config_orm)

        if orm.get(engine_name, None) is None:
            return False, "配置文件orm节点下不存在{}引擎".format(engine_name)

        return True, orm.get(engine_name)



