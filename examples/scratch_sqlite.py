"""Scratch Sqlite Auth Provider"""

import asyncio

from bareasgi_auth_server.auth_provider.sqlite_auth_provider import SqliteAuthProvider, Password

async def play_async():
    provider = SqliteAuthProvider("auth.db")
    await provider.initialise()

    pwd = Password(id=0, name='rob', salt='salt', hash='hash', state='active')
    await provider.create(pwd)
    print('done')

    pwd = Password(id=0, name='tom', salt='salt', hash='hash', state='active')
    await provider.create(pwd)
    print('done')

    try:
        pwd = await provider.read('foo')
        print(pwd)

        pwd = await provider.read('rob')
        print(pwd)

        pwd.hash = 'hsah'
        result = await provider.update(pwd)
        print(result)

        pwd.name = 'bor'
        result = await provider.update(pwd)
        print(result)

        result = await provider.delete(pwd.id)
        print(result)

        result = await provider.delete(pwd.id)
        print(result)

    except Exception as error:
        print(error)

async def init_async():
    provider = SqliteAuthProvider("auth.db")
    await provider.initialise()

    admin = await provider.create(Password.create('admin', 'trustno1', 'active'))
    print(admin.is_valid_password('trustno1'))
    rtb = await provider.create(Password.create('rtb', 'thereisnospoon', 'active'))
    print(rtb.is_valid_password('thereisnospoon'))
    print('done')

        
asyncio.run(init_async())