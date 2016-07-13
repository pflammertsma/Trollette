#! /usr/bin/python
# Requires wikipedia.py, wiki2plain.py, and python yaml
import wikipedia
import os
import sys
import unicodedata
from random import randint as rand


class Face:
    def __init__(self, topic):
        self.content = ''
        self.topic = topic

        self.uncertain = ' can mean many things, but to me it is'
        self.unknown = ' is a difficult concept to grasp'

        if self.topic:
            self.content = self.get_text()

    def set_topic(self, new_topic):
        self.topic = new_topic
        topic_path = os.path.join("Content", "%s.txt" % new_topic)
        if os.path.exists(topic_path):
            with open(topic_path, "r") as f:
                self.content = f.read()
        else:
            self.content = self.get_text()

    def get_text(self):

        try:
            # do a wikipedia search for the topic
            topic_results = wikipedia.search(self.topic)

            # pick one of the results and grab the content
            self.content += wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content

            # DO IT MORE
            more_content = wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content
            if more_content not in self.content:
                self.content += more_content
            more_content = wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content
            if more_content not in self.content:
                self.content += more_content
            more_content = wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content
        except wikipedia.exceptions.DisambiguationError as e:
            self.content += self.topic + self.uncertain
        except wikipedia.exceptions.PageError as e:
            self.content += self.topic + self.unknown

        # if there are more than one word in the topic try to get some more results with the first and last word
        if len(self.topic.split()) > 1:
            try:
                # get more results with less of the topic for some ambiguity
                topic_results = wikipedia.search(self.topic.split()[:1])
                self.content += wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content
                more_content = wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content
                if more_content not in self.content:
                    self.content += more_content
            except wikipedia.exceptions.DisambiguationError as e:
                self.content += self.topic + self.uncertain
            except wikipedia.exceptions.PageError as e:
                self.content += self.topic + self.unknown
            try:
                # get even more with the second half of the topic for wierd results maybe
                topic_results = wikipedia.search(self.topic.split()[-1:])
                self.content += wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content
                more_content = wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content
                if more_content not in self.content:
                    self.content += more_content
            except wikipedia.exceptions.DisambiguationError as e:
                self.content += self.topic + self.uncertain
            except wikipedia.exceptions.PageError as e:
                self.content += self.topic + self.unknown
        try:
            # do a wikipedia search for the topic
            topic_results = wikipedia.search(self.topic[:len(self.topic) / 2])

            # pick one of the results and grab the self.content
            self.content += wikipedia.page(topic_results[rand(0, len(topic_results) - 1)]).content
        except wikipedia.exceptions.DisambiguationError as e:
            self.content += self.topic + self.uncertain
        except wikipedia.exceptions.PageError as e:
            self.content += self.topic + self.unknown

        return self.content.capitalize()

    def research_topic(self, topic, logger):
        content = ""

        # do a wikipedia search for the topic
        topic_results = wikipedia.search(topic)

        logger("  Search returned %d articles on %s" % (len(topic_results), topic))
        for i in range(len(topic_results)):
            try:
                data = wikipedia.page(topic_results[i]).content
                if type(data) is str:
                    content += data
                elif type(data) is unicode:
                    content += unicodedata.normalize('NFKD', data).encode('ascii', 'ignore')
            except:
                pass

        return content.capitalize()

    def fully_research_topic(self, topic, logger):
        content = self.research_topic(topic, logger)

        #except wikipedia.exceptions.DisambiguationError as e:
        #    self.content += topic + ' can mean many things but to me it is'
        #except wikipedia.exceptions.PageError as e:
        #    self.content += topic + ' is sometimes hard to find'
        #except Exception as e:
        #    print e

        # if there are more than one word in the topic try to get some more results with the first and last word
        topic_split = topic.split()
        if len(topic_split) > 1:
            for i in range(len(topic_split)):
                try:
                    # Skip words that are less than five characters
                    if len(topic_split[i]) < 3:
                        continue

                    content += self.research_topic(topic_split[i], logger)

                except wikipedia.exceptions.DisambiguationError as e:
                    content += topic + self.uncertain
                except wikipedia.exceptions.PageError as e:
                    content += topic + self.unknown

        return content.capitalize()

    def parse_text(self):
        phrases = []
        words = self.content.split()
        # function to take a blob and parse out apropriately sized snippets
        for index in range(0, len(words) - 1):
            if self.topic.lower()[:len(self.topic) / 4] in words[index].lower() or self.topic.split()[-1].lower() in \
                    words[index].lower():
                cur_word = words[index]
                phrase = ''
                if index > 5:
                    i = index - rand(0, 5)
                else:
                    i = index
                counter = 0
                while cur_word.isalpha() and counter < 6:
                    try:
                        phrase = phrase + words[i].lower()
                        i += 1
                        cur_word = words[i]
                    except:
                        cur_word = '...'
                    counter += 1
                if len(phrase.split()) > 3:
                    temp = ''
                    for char in phrase:
                        if char.isalpha() or char.isspace():
                            temp += char
                    phrase = temp
                    if (rand(0, 12) < 3):
                        other_words = ['Clearly, ', 'As I said, ', 'Therefore, ', 'Until now, ',
                                       'Ultimately, ', 'A.K.A. ', 'In other words, ', 'Our response: ',
                                       'An example: ', 'According to sources, ']
                        phrase = other_words[rand(0, len(other_words) - 1)] + phrase
                    elif (rand(0, 12) < 3):
                        other_words = [', but in reality it wasn\'t', ' was not the case',
                                       '... or not', ', right?', '... WTF!', 
                                       ', according to sources', ', experts say', 
                                       '!', '!!!', '?!', '?']
                        phrase = phrase + other_words[rand(0, len(other_words) - 1)]
                    phrases.append(phrase.capitalize())
        phrases = list(set(phrases))
        return phrases

    def parse_bullets(self):
        bullets = []
        sentences = self.content.split('.')
        for ea in sentences:
            if len(ea) in range(50,75) and "\n" not in ea and "=" not in ea:
                bullets.append(ea)
        return bullets

    def get_bullets(self, min_count):
        final_bullets = []
        while len(final_bullets) < min_count:
            self.content += self.get_text()
            bullets = self.parse_bullets()
            for b in bullets:
                final_bullets.append(b.strip())
        return final_bullets

    def get_titles(self, min_count):
        # function to choose short headlines for the top of slides
        headlines = []
        while len(headlines) < min_count:
            self.content += self.get_text()
            phrases = self.parse_text()
            for p in phrases:
                headlines.append(p.strip())
        return headlines
