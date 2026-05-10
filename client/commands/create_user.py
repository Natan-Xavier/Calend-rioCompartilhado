from client.commands.base import ICommand


class CreateUserCmd(ICommand):
    def __init__(self, proxy):
        self.proxy = proxy

    def execute(self):
        name = input("Nome: ")
        email = input("Email: ")
        data, status = self.proxy.create_user(name, email)
        if status == 201:
            print(f"✅ Usuário '{data['name']}' criado com sucesso!")
        else:
            print(f"❌ Erro ao criar usuário: {data}")