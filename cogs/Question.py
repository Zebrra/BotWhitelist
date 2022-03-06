#! /usr/bin/python3
# -*- coding: utf-8 -*-

from typing import Any

class Question:
    """
    Initialisation de l'objet Question (prompt, answer_prompt, answer)

    viens prendre 
    ```
    def __init__(self, prompt, answer_prompt, answer)
    ```
    """

    def __init__(self, prompt: Any, answer_prompt: Any, answer: Any) -> Any:
        self.prompt = prompt
        self.answer_prompt = answer_prompt
        self.answer = answer