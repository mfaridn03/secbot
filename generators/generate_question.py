import random
import string

import discord

numbers = set([x for x in '123456789'])
letters = set([x for x in string.ascii_letters])

all_sum_question = [  # num1, operator, num2
    "In a math test, you see this: **Q{2}**. What is the sum of {0} and {1}?\nWhat is the answer?",
    "{0} + {1} = ? \nTake your time, you have {2} years (no you don't)",
    "Solve this: {0} + {1} = ? (The answer is not {2} by the way)",
    "**Random question #{2}**\nWhat do you get after adding {0} with {1}?",
    "Jack has {0} apples. Jill has {1} apples from a pool of {2} apples. How many apples do they have in total?",
    "Out of {2} marbles, Bob took {0} and Catherine took {1}. How many did they took?"
]


async def create_question(member):
    emb = discord.Embed(
        title='Captcha Verification',
        colour=0xff0000
    )
    choose_type = random.randint(1, 2)  # 1 is math, 2 is count number
    if choose_type == 1:
        random_numb = random.randint(30, 90)
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)

        q = random.choice(all_sum_question)
        emb.description = q.format(num1, num2, random_numb)
        await member.send(
            embed=emb
        )
        return str(num1 + num2)  # Answer of the Q

    else:
        random_numb = str(random.randint(1000, 1000000) * 31415926)
        format_q = '  '.join([x for x in random_numb if x != '0'])

        math_type = random.randint(1, 2)

        if math_type == 1:  # Count odd nums
            correct_ans = len([n for n in random_numb if n != '0' and int(n) % 2 > 0])
            emb.description = f"How many **odd** numbers are there in this sequence:\n{format_q}"

            await member.send(
                embed=emb
            )
            return str(correct_ans)

        else:  # Count even nums
            correct_ans = len([n for n in random_numb if not int(n) % 2 == 0])
            emb.description = f"How many **odd** numbers are there in this sequence:\n{format_q}"

            await member.send(
                embed=emb
            )
            return str(correct_ans)
