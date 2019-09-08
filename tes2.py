import handlers.sauce.get_source as gs
import handlers.sauce.comment_builder as bc

a = gs.get_source_data("https://res.cloudinary.com/fuwa/image/upload/v1567928580/U2e91a820fc12fa78c55ded8731cd3698.jpg", trace=True)
a = bc.build_comment(a)

print(a)
