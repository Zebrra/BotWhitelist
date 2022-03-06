#! /usr/bin/python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv('config/.env'))


class ExternFiles:
    """## Classe mère.

    #### ``self.__string_property`` est la string temporaire pour la fonction ``get_path(self)``
    #### Cette string est utilisée lors de l'instanciation de la classe mère dans les classes filles.
    ```
    get_path(self) -> str:
        \"\"\"Fais abstraction du .env\"\"\"
        return os.environ[self.__string_property]
    ```
    Permet de faire l'abraction du .env en ne renseignant que la chaîne de lien.
    """
    
    def __init__(self, string_property: str) -> str:
        self.__string_property = string_property

    def get_path(self) -> str:
        """Fais abstraction du .env"""
        return os.environ[self.__string_property]



class Database(ExternFiles):
    """## Classe fille

    #### ``self.__string_property``devient le lien vers le ``.env``
    
    ```
    def __init(self):
        self.__string_property = 'DATABASE_NAME'
    ```

    - Viens donc appeler la classe mère avec les méthodes.
    
    ```
    get_prefix_path(self) -> str ou int:
        return Files(self.__string_property).get_path()
    ```
    """
    def __init__(self):
        self.__string_property = 'DATABASE_NAME'
        # self.__path_file = ExternFiles(self.__string_property)

    def get_database_path(self) -> str:
        """Appel la méthode get_path() de la classe mère."""
        # return self.__path_file.get_path()
        return ExternFiles(self.__string_property).get_path()

class PrefixJson(ExternFiles):
    """### Classe fille
    ```
    self.__string_property = 'JSON_PREFIX_NAME'
    
    def get_prefix_path(self) -> str:
    ```
    """
    def __init__(self):
        self.__string_property = 'JSON_PREFIX_NAME'
    
    def get_prefix_path(self) -> str:
        return ExternFiles(self.__string_property).get_path()

class WriteQuestionsJson(ExternFiles):
    """### Classe fille
    ```
    self.__string_property = 'JSON_WRITE_QUESTIONS'
    
    def get_write_questions_path(self) -> str:
    ```
    """
    def __init__(self):
        self.__string_property = 'JSON_WRITE_QUESTIONS'
    
    def get_write_questions_path(self) -> str:
        return ExternFiles(self.__string_property).get_path()

class ReactQuestionsJson(ExternFiles):
    """### Classe fille
    ```
    self.__string_property = 'JSON_REACT_QUESTIONS'
    
    def get_react_questions_path(self) -> str:
    ```
    """
    def __init__(self):
        self.__string_property = 'JSON_REACT_QUESTIONS'
    
    def get_react_questions_path(self) -> str:
        return ExternFiles(self.__string_property).get_path()




class NumberQuestion(ExternFiles):
    """### Classe fille
    ```
    self.__string_property = 'NUMBER_QUESTIONS'

    def number_question(self) -> int:
    ```
    """
    def __init__(self):
        self.__string_property = 'NUMBER_QUESTIONS'

    def number_question(self) -> int:
        return int(ExternFiles(self.__string_property).get_path())

class GuildId(ExternFiles):
    """### Classe fille
    ```
    self.__string_property = 'GUILD_ID'

    def get_guild_id_path(self) -> int:
    ```
    """
    def __init__(self):
        self.__string_property = 'GUILD_ID'

    def get_guild_id_path(self) -> int:
        return int(ExternFiles(self.__string_property).get_path())

class Token(ExternFiles):
    """### Classe fille
    ```
    self.__string_property = 'TOKEN'

    def get_token_path(self) -> str:
    ```
    """
    def __init__(self):
        self.__string_property = 'TOKEN'
    
    def get_token_path(self) -> str:
        return ExternFiles(self.__string_property).get_path()
    


if __name__ == '__main__':
    database = Database()
    print(database.get_database_path())

    prefix_json = PrefixJson()
    print(prefix_json.get_prefix_path())

    
    print(GuildId().get_guild_id_path())
    print(Token().get_token_path())