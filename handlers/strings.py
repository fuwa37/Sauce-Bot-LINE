s_commands = {'!sauce',
              '!sauce-anime-ext',
              '!sauce-anime-ext+'}

h_commands = {'!(',
              '!)',
              '!}',
              '!!'}
robo_commands = {'!{',
                 '!<',
                 '![',
                 '!]'}

help_reply = "1. Send image\n" \
             "2. Type command:\n" \
             "- !sauce - general sauce\n\n" \
             "- !kikku - leave group/room"

help_sukebei = "Sukebei Commands:\n" \
               "- !(<numbers>) - nHentai\n" \
               "example: !(123456) or !(00001)\n\n" \
               "- !)<numbers>( - Tsumino\n" \
               "example: !)12345( or !)00002("

help_sukebei_ext = "For nHentai galleries you need to put the gallery number in parentheses, " \
                  "while padding it with leading zeroes to have at least 5 digits. For example: (123456) or (00001)\n" \
                  "For Tsumino galleries you need to put the gallery number in inverted parentheses, " \
                  "while padding it with leading zeroes to have at least 5 digits. For example: )12345( or )00002("

base_url = "https://res.cloudinary.com/fuwa/image/upload/v"
