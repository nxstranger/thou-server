import graphene
from graphql_jwt.decorators import login_required


class SayHello(graphene.Mutation):

    class Arguments:
        name = graphene.String()

    message = graphene.String()

    # @login_required
    def mutate(self, info, name):
        answer = 'Hello {}'.format(name)
        return SayHello(message=answer)


class ChatUserChangeContact(graphene.Mutation):

    class Arguments:
        contact_name = graphene.String(required=True)

    status = graphene.Boolean()

    @login_required
    def mutate(self, info, contact_name):
        print(self)
        return ChatUserChangeContact(status=True)
