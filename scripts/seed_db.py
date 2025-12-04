#!/usr/bin/env python
"""Script para popular o banco de dados com dados de exemplo.

Uso:
  python scripts/seed_db.py

Ele usa Django settings definidos em `config.settings`.
"""
import os
import random
import sys
from pathlib import Path

# Garantir que o diretório raiz do projeto esteja no path para importar o pacote config
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from livros.models import Autor, Genero, Livro
from django.contrib.auth import get_user_model


def create_authors(names):
    created = []
    for n in names:
        obj, _ = Autor.objects.get_or_create(nome=n)
        created.append(obj)
    return created


def create_genres(names):
    created = []
    for n in names:
        obj, _ = Genero.objects.get_or_create(nome=n)
        created.append(obj)
    return created


def create_books(count, authors, genres, states):
    created = []
    for i in range(1, count + 1):
        titulo = f"Livro Exemplo {i}"
        autor = random.choice(authors)
        genero = random.choice(genres)
        estado = random.choice(states)
        disponivel = random.choice([True, True, False])  # mais provavel disponivel

        book, created_flag = Livro.objects.get_or_create(
            titulo=titulo,
            defaults={
                'autor': autor,
                'genero': genero,
                'estado': estado,
                'disponivel': disponivel,
            }
        )
        if not created_flag:
            # se já existia, atualiza campos básicos
            book.autor = autor
            book.genero = genero
            book.estado = estado
            book.disponivel = disponivel
            book.save()

        created.append(book)
    return created


def create_test_user(username='admin', password='admin123'):
    User = get_user_model()
    user, created = User.objects.get_or_create(username=username, defaults={'is_staff': True, 'is_superuser': True, 'email': f'{username}@example.com'})
    if created:
        user.set_password(password)
        user.save()
    return user, created


def main():
    authors = [
        'Machado de Assis',
        'Clarice Lispector',
        'Jorge Amado',
        'Paulo Coelho',
        'Monteiro Lobato',
    ]

    genres = [
        'Romance',
        'Ficção',
        'Infantil',
        'Economia',
        'História',
    ]

    states = ['Novo', 'Usado', 'Danificado']

    print('Criando autores...')
    authors_objs = create_authors(authors)
    print(f'Autores: {len(authors_objs)}')

    print('Criando gêneros...')
    genres_objs = create_genres(genres)
    print(f'Gêneros: {len(genres_objs)}')

    print('Criando usuário de teste...')
    user, user_created = create_test_user()
    print(f'Usuário {user.username} - criado: {user_created}')

    print('Criando livros de exemplo...')
    books = create_books(30, authors_objs, genres_objs, states)
    print(f'Livros criados/atualizados: {len(books)}')

    print('Resumo final:')
    print('  Autores no DB:', Autor.objects.count())
    print('  Gêneros no DB:', Genero.objects.count())
    print('  Livros no DB:', Livro.objects.count())


if __name__ == '__main__':
    main()
