import yaml
import os
import chardet
import codecs


class ConfigNotFound(Exception):
    def __init__(self, config):
        self.config = config

    def __str__(self):
        return "配置文件[{}]不存在".format(self.config)


class ConfigParseError(Exception):
    def __init__(self, config):
        self.config = config

    def __str__(self):
        return "配置文件[{}]解析错误".format(self.config)


class SectionNotExists(Exception):
    def __init__(self, section):
        self.section = section

    def __str__(self):
        return "配置文件读取错误。不存在的配置项[{}]".format(self.section)


class EngineNotExists(Exception):
    def __init__(self, engine):
        self.engine = engine

    def __str__(self):
        return "数据库引擎配置读取错误。不存在的引擎[{}]".format(self.engine)


class Config:

    _config_file = "TransTools.yaml"
    _config_encoding = "utf-8"
    _config_orm = "orm"
    _orm_default = "default"

    def get_config(self):
        """获取配置文件，并解析为python对象"""
        if not os.path.exists(self._config_file):
            raise ConfigNotFound(self._config_file)
        with open(self._config_file, 'rb') as f:
            encoding = chardet.detect(f.read())['encoding']
        with codecs.open(self._config_file, encoding=encoding) as f:
            try:
                y = yaml.load(f)
            except Exception as e:
                raise ConfigNotFound(self._config_file)
            return y

    def get_orm_engine(self, engine_name=None):
        """获取orm引擎"""
        if engine_name is None:
            engine_name = self._orm_default

        config = self.get_config()

        if config.get(self._config_orm, None) is None:
            raise SectionNotExists(self._config_orm)

        orm = config.get(self._config_orm, None)
        if orm is None:
            raise SectionNotExists(self._config_orm)

        if orm.get(engine_name, None) is None:
            raise EngineNotExists(engine_name)

        return orm.get(engine_name)


if __name__ == "__main__":
    config = Config()
    print(config.get_orm_engine("ps"))

