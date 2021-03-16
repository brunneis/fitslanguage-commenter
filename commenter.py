from requests import Session
import lxml.html
import yaml
import logging
import re
from random import randint, sample

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)-15s [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def get_comment(text, teacher_name):
    def get_random_sentence(sentences):
        return sentences[randint(0, len(sentences) - 1)]

    p1_sentences = [
        f'Good afternoon {teacher_name}! ',
        f'Hey {teacher_name}! ',
        f'{teacher_name}! ',
        f'Happy day {teacher_name}! ',
    ]
    p2_sentences = [
        'It was nice to attend to your class. ',
        'Nice class, as usual. ',
        'Great class! ',
        'I enjoyed today\'s class. ',
        'Liked the class. ',
    ]
    p3_sentences = [
        'Great! ',
        'Feedback is always welcome :) ',
        'Message received! ',
        'Thank you for your feedback. ',
        'Nice to read your feedback. ',
        'Thank you for your advice and corrections. ',
    ]
    p4_sentences = [
        'I found specially useful ',
        'I will try to fix my pronunciation with ',
    ]
    p5_sentences = [
        'Waiting for the next class. ',
        'Cheers! ',
        'See you in the next class! ',
        'Hear yah in the next class. ',
        'See you! ',
        'Have a nice day! ',
        'Bye! ',
        'See you soon! ',
        'See you later! ',
        'Goodbye! ',
        'Take care! :) ',
    ]

    comment = f'{get_random_sentence(p1_sentences)}'
    comment += f'{get_random_sentence(p2_sentences)}'
    comment += f'{get_random_sentence(p3_sentences)}'
    correction_pattern = re.compile(r'\([^\s]+-[^\s]+\)')
    results = re.findall(correction_pattern, text)
    corrections = [result[1:-1] for result in results]

    if corrections:
        max_corrections = 3 if len(corrections) > 3 else len(corrections)
        selected_corrections = sample(corrections, randint(1, max_corrections))

        comment += f'{get_random_sentence(p4_sentences)}'
        if len(selected_corrections) == 1:
            comment += selected_corrections[0] + '. '
        else:
            comment += ', '.join(selected_corrections[:-1])
            comment += f' and {selected_corrections[-1]}. '

    comment += f'{get_random_sentence(p5_sentences)}'
    return comment.replace('’', '\'').strip()


with open('config.yaml', 'r') as input_file:
    config = yaml.safe_load(input_file)

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
headers = {'user-agent': user_agent, 'Content-Type': 'application/x-www-form-urlencoded'}
session = Session()
session.headers.update(headers)

session.post('https://www.fitslanguage.com/login',
             data=f"email={config['email']}&pass={config['password']}&entrar=Iniciar sesión")

for page in range(1, int(config['pages']) + 1):
    response = session.get(f'https://www.fitslanguage.com/lessons/{page}')

    root = lxml.html.document_fromstring(response.content)
    buttons = root.xpath("//a[@class='ui blue button']")

    for button in buttons:
        class_id = button.xpath("./@href")[0].split('/')[-1]

        response = session.get(f'https://www.fitslanguage.com/lessons/view/{class_id}')
        root = lxml.html.document_fromstring(response.content)
        text = ' '.join(root.xpath("//div[@class='ui segment']/p/text()")).strip()
        class_teacher_name = root.xpath(
            "//div[@class='ui large header']/div[@class='content']/text()")[0].strip().lower(
            ).split()[1]

        is_available = root.xpath("//input[@class='ui primary button']")
        if is_available and class_teacher_name == config['teacher'].lower():
            comment = get_comment(text, config['teacher'])
            logging.info(f'[LINK] https://www.fitslanguage.com/lessons/view/{class_id}')
            logging.info(f'[EVALUATION] {text}')
            logging.info(f'[COMMENT] {comment}')
            response = session.post(
                'https://www.fitslanguage.com/lessons/rate',
                data=
                f'classID={class_id}&rate_1=5&rate_2=5&rate_3=5&rate_4=5&rate_5=5&rate_6=5&comment={comment}&saverate=Evaluar'
            )
            logging.info(f'[RESULT] [{response.status_code}]\n')
