import graphene
from chat.graphql.mitations import SayHello, ChatUserChangeContact


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hi!")


class Mutations(graphene.ObjectType):
    say_hello = SayHello.Field()
    chat_user_change_contact = ChatUserChangeContact.Field()


schema = graphene.Schema(query=Query, mutation=Mutations)

