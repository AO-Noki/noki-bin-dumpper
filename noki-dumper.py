import sys

"""Não escrever arquivos .pyc"""
sys.dont_write_bytecode = True

from noki.core.program import main

if __name__ == "__main__":
    main()
