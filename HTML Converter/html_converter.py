from bs4 import BeautifulSoup, NavigableString
import re
import os
import tkinter
from tkinter.filedialog import askdirectory
import itertools


def delete_element(my_soup, my_tag_name, my_class):
    for tag in my_soup.findAll(my_tag_name, class_=my_class):
        tag.decompose()


def unwrap_element(my_soup, my_tag_name, my_class):
    for tag in my_soup.findAll(my_tag_name, class_=my_class):
        tag.unwrap()


# sets the class equal to an empty string, ''
def remove_class(my_soup, my_tag_name, my_class):
    for tag in my_soup.findAll(my_tag_name, class_=my_class):
        tag['class'] = ''


# deletes the class entirely
def delete_class(my_soup, my_tag_name, my_class):
    for tag in my_soup.findAll(my_tag_name, class_=my_class):
        del tag['class']


def remove_line_breaks(string):
    string = re.sub(r'<\s*br\s*/?\s*>', '<br>', string)  # standardize line breaks
    string = re.sub(r'(\s<br>)|(<b>\s)', ' ', string)  # delete line breaks with a space on either side
    string = re.sub(r'<br>', ' ', string)  # delete line breaks with no spaces, and add a space
    return string


def clean_html_file(input_filename, output_filename_clean, output_filename_partially_clean):

    def clean(old_tag_name, classes_to_change, new_tag_name, classes_to_add):
        tags = []

        if type(classes_to_change) == 'str':
            tags = soup.findAll(old_tag_name, class_=classes_to_change)
        else:
            for current_class_name in classes_to_change:
                tags += soup.findAll(old_tag_name, class_=current_class_name)

        for tag in tags:
            if new_tag_name is not None:
                tag.name = new_tag_name
            if classes_to_add is None:
                del tag['class']
            else:
                tag['class'] = classes_to_add

    def clean_paragraphs(classes_to_change, new_tag_name, classes_to_add):
        clean('p', classes_to_change, new_tag_name, classes_to_add)

    def clean_span(classes_to_change, new_tag_name, classes_to_add):
        clean('span', classes_to_change, new_tag_name, classes_to_add)

    with open(input_filename, 'r', encoding='utf-8') as infile:

        soup = BeautifulSoup(infile, 'html.parser')

        # Stylesheet
        has_stylesheet = False
        for element in soup.findAll('link', rel='stylesheet', type='text/css'):
            element['href'] = 'styles.css'
            has_stylesheet = True
        if not has_stylesheet:
            stylesheet = BeautifulSoup('<link href="styles.css" rel="stylesheet" type="text/css"/>',
                                       features="html.parser")
            # try:
            #     soup.find('title').insert_after(stylesheet)
            # except AttributeError:
            #     soup.append(stylesheet)
            soup.find('title').insert_after(stylesheet)

        # Article Titles
        # ==> h1
        clean_paragraphs(['•title-one-line', '•Book-review-title', '•brief-notice-title', '•poetry-title',
                          '•title-one-line-w-subtitle', '•title-two-line', 'bn-title', 'notice-title'], 'h1', None)

        # remove header <a> tag
        for element in soup.findAll('a', id='_idTextAnchor000'):
            element.replaceWithChildren()


        # make standardize line breaks
        for header in soup.findAll('h1'):
            string = str(header)

            # standardize line breaks
            string = re.sub(r'< *br */? *>', '<br>', string)

            # move breaks from inside spans to outside spans
            string = re.sub(r'<span([a-zA-Z0-9"\'= ]*)><br>', '<br><span\1>', string)
            string = re.sub(r'<br></span>', '</span><br>', string)

            # remove line breaks from title
            string = remove_line_breaks(string)

            # replace title with clean title
            new_header = BeautifulSoup(string, features='html.parser')
            header.replace_with(new_header)

        # Subtitles
        # ==> p.subtitle
        clean_paragraphs(['•subtitle-index-volume-', '•subtitle-index-volume-','•subtitle', 'advertisement-heading_new-title'], None, 'subtitle')
        for subtitle in soup.findAll('p', class_='subtitle'):
            string = remove_line_breaks(str(subtitle))
            new_subtitle = BeautifulSoup(string, features='html.parser')
            subtitle.replace_with(new_subtitle)



    # Document Title
        # (for document transcriptions)
        clean_paragraphs(['•dc-title-of-document','•title'], None, 'document-title')

        # Author
        # ==> p.author
        clean_paragraphs(['advertisement-heading_new-author','•author-w-title', '•book-reviewer', '•author-w-two-line-title',
                          '•author-w-title---sub ParaOverride-1', '•author-w-title---sub','•author'], None, 'author')

        # Author for Book Notices
        # ==> p.author-book-notice
        clean_paragraphs(['•brief-notices-byline'], None, 'author-book-notice')

        # Publication Information
        # ==> p.publication-info
        clean_paragraphs(['•Book-review-title-2nd-line', 'advertisement-heading_pub-info'], None, 'publication-info')

        # Level 1 Headers
        # ==> h2
        clean_paragraphs(['•subhead--0-', 'Heading-1-Text','nonheading','h2'], 'h2' , None)

        # Level 2 Headers
        # ==> h3
        clean_paragraphs(['•subhead--1-'], 'h3', None)

        # Level 3 Headers
        clean_paragraphs(['•subhead--2-','volumes','volume-hanging','subhead2','Headings', 'ordering-fine-print'], 'h4', None)

        # Default Paragraphs
        clean_paragraphs(['•1st-paragrph', 'Normal-no-indent', '•brief-notices-no-indent','body-text-no-indent',
        '•brief-notices-text','comparisons','notict-title'], 'p', None)
        clean_paragraphs(['Normal'], 'p', 'indent-1-0')

        # 1-0 First Line Indent
        clean_paragraphs(['•brief-notices-indent', 'inline-subhead'], None, 'indent-1-0')

        #1-2 Hanging Indent Begin
        # (first line indented once, all other lines indented twice)
        clean_paragraphs(['•10-5-Hanging-Indent-Paragraph'], None,'indent-1-2 begin')

        # 1-2 Hanging Indent
        clean_paragraphs(['•10-5-Hanging-IndPar-Middle','•10-5-Hanging-interior-para','•Hanging-Indent-Paragraph',
                          '•Hanging-Indent-Paragraph--small-', '•Hanging-IndPar-Middle', 'example-lines', 'list-subparagraph'], None,
                         'indent-1-2')

        # 1-2 Hanging Indent with Space after paragraph
        clean_paragraphs(['•10-5-Hanging-IndPar-End', '•10-5-Hanging-IndPar-End-5-5', '•Hanging-IndPar-End','subhanging'], None,
                         'indent-1-2 end')

        # 2-3 Hanging Indent
        # (first line indented twice, all other lines indented three times)
        clean_paragraphs(['example-lines-extra-space','double-indent'], None, 'indent-2-3')

        # 3-4 Hanging Indent
        # (first line indented three times, all other lines indented four times)
        clean_paragraphs(['example-lines-extra-indent---space'], None, 'indent-3-4')

        # 4-5 Hanging Indent
        # (first line indented four times, all other lines indented five times)
        clean_paragraphs(['example-comment'], None, 'indent-4-5')

        # 3-3 Paragraph Indent
        clean_paragraphs(['sub-paragraph'], None, 'indent-3-3')

        #Script to make all indent-1-2 class in to an ordered list
        element = soup.findAll('p',class_='indent-1-2 begin')
        for el in element:
            siblings = [sibling for sibling in el.next_siblings if type(sibling)!= NavigableString]
            # list of all next_siblings class
            # li = [s['class']for s in siblings if 'class'in s.attrs]
            # print(li[:3])
            els = [i for i in itertools.takewhile(
                lambda x: 'class'in x.attrs and 'indent-1-2' in x['class'], siblings)]
            ol = soup.new_tag('ul')
            el.wrap(ol)
            for child in els:
                ol.append(child)

        # Publication Lines
        # (first line indented once, second line indented past half the page width)
        clean_paragraphs(['publication-lines'], None, 'publication-lines')

        # Block Quotes
        clean_paragraphs(['•quote-5-5-no-indent', '•quote-no-indent', '•quote-center', '•block-quote-center',
                          '•block-quote', '•block-quote-5-5', '•block-quote-end--5'], None, 'block-quote')

        # Script to remove all <p class="block-quote"> to <blockquote>
        for element in soup.findAll('p', class_='block-quote'):
            del element['class']
            element.name = 'blockquote'


        # Block Quotes with space above paragraph
        clean_paragraphs(['•quote-begin-no-indent', '•block-quote-begin'], None, 'block-quote begin')

        # Script to remove all <p class="block-quote"> to <blockquote>
        for element in soup.findAll('p', class_='block-quote begin'):
            del element['class']
            element.name = 'blockquote'

        # Block Quotes with Space after paragraph
        clean_paragraphs(['•quote-end', '•quote-end--5', '•block-quote-end'], None, 'block-quote end')

        # Script to remove all <p class="block-quote"> to <blockquote>
        for element in soup.findAll('p', class_='block-quote end'):
            del element['class']
            element.name = 'blockquote'

        # Block Quotes with Indent
        # ==> p.block-quote.block-quote-indent
        clean_paragraphs(['•quote-indent', '•quote-5-5-indent', '•quote-begin-indent'], None,
                         'block-quote block-quote-indent')

        # Script to remove all <p class="block-quote block-quote-indent"> to <blockquote>
        for element in soup.findAll('p', class_='block-quote block-quote-indent'):
            del element['class']
            element.name = 'blockquote'


        # Block Quote with Indent and Space above paragraph
        clean_paragraphs(['•quote-begin-indent'], None,
                         'block-quote block-quote-indent begin')

        # Superscript
        clean_span(['superscript-letters', 'superscript'], None, 'superscript')
        # Script to remove all <span> to <sup>
        for element in soup.findAll('span', class_='superscript'):
            del element['class']
            element.name = 'sup'

        # Underline
        clean_span(['underlined','ital-underline'], None, 'underline')
        # Script to remove all <span class ="underline" > to <ins>
        for element in soup.findAll('span', class_='underline'):
            del element['class']
            element.name = 'ins'

        # Underlined Superscripts
        clean_span(['underlined-superscript'], None, 'underline superscript')
        # Wrap a strong tag around <span class_='underline superscript'/>
        for element in soup.findAll('span', class_='underline superscript'):
            string = str(element)
            parse = BeautifulSoup(string, features="html.parser")
            if parse is not None:
                new_string = parse.span.wrap(parse.new_tag('ins'))
                element.replace_with(new_string)
            # remove <span class_='underline superscript/> and convert to <sup>
            tag = soup.find('span', class_='underline superscript')
            del tag['class']
            tag.name = 'sup'


        # Small Caps
        for element in soup.findAll('span', class_='all-small-caps'):
            string = str(element.string)
            if string is not None and string.isupper():
                element.unwrap()
            else:
                element['class'] = 'small-caps'

        # Italics
        clean_span(['italic', 'Emphasis', 'table-italic', 'tables_table-heads-italic','tabular-figures','TNR-ital','scriptures','link-italic', 'ital'], None, 'italics')

        # Script to remove all <span class="italics"> to <em>
        for element in soup.findAll('span', class_='italics'):
            del element['class']
            element.name = 'em'

        # Bold
        clean_span(['Minion-Semibold', 'Minion-Semibold-SC', 'Minion-bold', 'semibold', 'table-bold'], None, 'bold')

        # Script to remove all <span class="bold"> to <em>
        for element in soup.findAll('span', class_='bold'):
            del element['class']
            element.name = 'strong'

        # Bold Italics
        clean_span(['bold-italic', 'Minion-Semibold-italic', 'boldItalic', 'boldItal','Minion-Bold-Italic','Minion-bold-italic','Minion-bold-ital','table-bold-ital', 'table-bold-italic'], None, 'bold italics')

        # Wrap a strong tag around <span class_='bold italics'/>
        for element in soup.findAll('span', class_='bold italics'):
            string = str(element)
            parse = BeautifulSoup(string, features="html.parser")
            if parse is not None:
                new_string = parse.span.wrap(parse.new_tag("strong"))
                element.replace_with(new_string)
            tag = soup.find('span', class_='bold italics')
            del tag['class']
            tag.name = 'em'
        clean_paragraphs(['bold italics'], None, None)  # remove all bold italics class tags

        # Footnotes Links
        for element in soup.findAll('a', class_='_idFootnoteLink _idGenColorInherit'):
            element['class'] = 'footnote-link'
            #adjust href so anchor tags work on website
            holder = str(element['href'])
            seperated = holder.split("#")
            holder = "#" + seperated[1]
            element['href'] = holder


        # Bold Underline
        clean_span(['bold-underline'], None, 'bold underline')

        # Wrap a strong tag around <span class_='bold underline'/>
        for element in soup.findAll('span', class_='bold underline'):
            string = str(element)
            parse = BeautifulSoup(string, features="html.parser")
            if parse is not None:
                new_string = parse.span.wrap(parse.new_tag('strong'))
                element.replace_with(new_string)
            tag = soup.find('span', class_='bold underline')
            del tag['class']
            tag.name = 'ins'
        clean_paragraphs(['bold underline'], None, None)


    # Bold Strikethrough
        clean_span(['bold-strikethrough'], None, 'bold strikethrough')
        # Wrap a strong tag around <span class_='bold strikethrough'/>
        for element in soup.findAll('span', class_='bold strikethrough'):
            string = str(element)
            parse = BeautifulSoup(string, features="html.parser")
            if parse is not None:
                new_string = parse.span.wrap(parse.new_tag('strong'))
                element.replace_with(new_string)
            tag = soup.find('span', class_='bold strikethrough')
            del tag['class']
            tag.name = 'del'
        clean_paragraphs(['bold strikethrough'], None, None)


    # Hebrew
        clean_span(['Hebrew-TNR', 'TNR-Hebrew', 'TNR'], None, 'hebrew')

        # Foreign
        clean_span(['vowel'], None, 'foreign')

        # Subscript
        clean_span(['subscript'], None, 'subscript')

        # Script to remove all <span class="subscript"> to <sup>
        for element in soup.findAll('span', class_='subscript'):
            del element['class']
            element.name = 'sup'

        # Horizontal Line
        # ==> hr
        for element in soup.findAll('hr', class_='HorizontalRule-1'):
            del element['class']

        # Links
        for element in soup.findAll('span', class_='link'):
            element.unwrap()

    # Author Bio
        # ==> p child of div.author-bio
        first_bioline = soup.find('p', class_=['•bioline', 'advertisement-heading_pub-info'])  # grab the first p.•bioline tag
        if first_bioline is not None:  # make sure there was a p.•bioline
            author_bio = soup.new_tag('div')  # create a new div
            author_bio['class'] = 'author-bio'  # give the div the class .author-bio
            first_bioline.insert_before(author_bio)  # insert the div.author-bio before the p.•bioline tag

            biolines = soup.findAll('p', class_='•bioline')  # grab all the p.•bioline tags
            for bioline in biolines:  # loop through them
                element = bioline.extract()  # extract each tag
                author_bio.append(element)  # append each tag to the div.author-bio

            clean_paragraphs(['•bioline'], None, None)  # remove all .•bioline class tags

        # Footnotes Links
        for element in soup.findAll('a', class_='_idFootnoteLink _idGenColorInherit'):
            element['class'] = 'footnote-link'
             #adjust href so anchor tags work on website
            holder = str(element['href'])
            seperated = holder.split("#") 
            holder = "#" + seperated[1]
            element['href'] = holder


        for element in soup.findAll('span', class_='Note-reference'):
            element.unwrap()

        unwrap_element(soup, 'span', 'Endnote-reference')
        unwrap_element(soup, 'span', 'Footnote-reference')

        # Find the correct footnote id and replace with supscript native tag
        for element in soup.findAll('span'):
            if element.get('id') is not None and re.match(r'footnote-[0-9]{3}-backlink', element.get('id')):
                element.contents[0]['id'] = element['id']
                del element['id']
                element.name = 'sup'

        # Footnotes
        for element in soup.findAll('div', class_='_idFootnotes'):
            element['class'] = 'all-footnotes'

        for element in soup.findAll('div', class_='_idFootnote'):
            element['class'] = 'footnote-body'

        clean_paragraphs(['•endnotes', '•endnotes-in', '•endnotes-in-2'], None, None)

        for element in soup.findAll('a', class_='_idFootnoteAnchor _idGenColorInherit'):
            del element['class']

            #adjust href so anchor tags work on website
            holder = str(element['href'])
            seperated = holder.split("#") 
            holder = "#" + seperated[1]
            element['href'] = holder

        unwrap_element(soup, 'span', 'Footnote-Reference')
        unwrap_element(soup, 'span', 'Footnote-Reference-no-super')
        unwrap_element(soup, 'span', 'Endnote-Reference')

        # Footnote Return Links
        for element in soup.findAll('span', class_='return-link'):

            # make sure we have a <span class='return-link'>^</span>
            if element.string != '^':
                continue

            # make sure that the element's parent is an <a>
            if element.parent.name != 'a':
                continue

            # make sure that the anchor tag has an href attribute
            href = element.parent.get('href')
            if href is None:
                continue

            # select the grandparent, then remove the parent
            grandparent = element.parent.parent
            element.parent.decompose()

            # move the return link to the right spot
            grandparent_string = re.sub(r'>([0-9\-]{1,7})\.', '><a href="' + str(href) + r'">\1.</a>',
                                        str(grandparent))

            # replace the old elements with the new ones
            new_grandparent = BeautifulSoup(grandparent_string, features="html.parser")
            grandparent.replace_with(new_grandparent)

        # delete any remaining span elements with the return-link class
        delete_element(soup, 'span', 'return-link')

        # Appendix Title
        clean_paragraphs(['•appendix-title'], None, 'appendix-title')

        # Bibliography Entries
        clean_paragraphs(['bibliography'], None, 'bibliography-entry')
        clean_paragraphs(['tables_table-heads-italic'], None, 'italics')

        # Images
        for element in soup.findAll('div', class_=['graphic-frame', 'graphic']):
            element['class'] = 'graphic-frame'
        for element in soup.findAll('img'):
            del element['class']
            element['src'] = ''
            parent = element.parent
            if parent.name == 'div' and 'graphic-frame' in parent['class']:
                grandparent = parent.parent
                if grandparent.name == 'div':
                    grandparent['class'] = ['graphic-frame-outer', 'invisible']
        for element in soup.findAll('div', class_='Basic-Graphics-Frame'):
            element['class'] = 'graphic-frame'

        # Inline Graphics
        clean_paragraphs(['inline-graphic'], None, 'inline-graphic')

        # Captions
        clean_paragraphs(['•caption'], None, 'caption')
        # Caption Frames
        for element in soup.findAll('p'):
            if element.get('class') == 'caption':
                parent_class = element.parent.get('class')
                if '_idGenObjectStyleOverride-1' in parent_class or 'Basic-Text-Frame' in parent_class:
                    element.parent['class'] = 'caption-frame'
        # Make Sure Caption Frames are inside graphic-frame-outer
        for element in soup.findAll('div'):
            if element.get('class') is not None and 'graphic-frame-outer' in element.get('class'):
                next_sibling = element.findNextSibling()
                if next_sibling is None:
                    continue
                if next_sibling.get('class') is not None and 'caption-frame' in next_sibling.get('class'):
                    next_sibling = next_sibling.extract()
                    element.append(next_sibling)

        # Author Abstract
        for element in soup.findAll('div', class_='_idGenObjectStyleOverride-1'):

            # check if the div has a p child
            first_child = element.find('p')
            # if not, skip that div
            if first_child is None:
                continue

            # get the class of the p child
            child_class = first_child.get('class')
            # if the p child has the class of 'sidebar-no-indent', change the div's class to 'author-abstract'
            # and change the classes of all its p children to 'author-abstract-body'
            if child_class is not None and 'sidebar-no-indent' in child_class:

                element['class'] = 'author-abstract'

                for child in element.findAll('p'):
                    child['class'] = 'author-abstract-body'

                author_div = element.findNextSibling('div').findNextSibling('div')
                author_div_class = author_div.get('class')
                if author_div_class is not None and '_idGenObjectStyleOverride-1' in author_div_class:
                    author_paragraph = author_div.find('p', class_='sidebar-title')
                    if author_paragraph is not None:
                        author_paragraph = author_paragraph.extract()
                        author_paragraph['class'] = 'author-abstract-title'
                        element.insert(0, author_paragraph)

                author_abstract = element.extract()
                for div in soup.body.findAll('div'):
                    if div.get('class') == 'author-bio':
                        div.insert_before(author_abstract)

        for element in soup.findAll('div', class_='_idGenObjectStyleOverride-5'):
            element['class']= '_idGenObjectStyleOverride-1'

        # Tables
        for element in soup.findAll(['table', 'td', 'tr'], class_=['shaded-table', 'Basic-Table', 'No-Table-Style', 'blank','Table-Section-Heading ']):
            del element['class']
        # Col
        for element in soup.findAll('col'):
            if element.attr is None:
                element.decompose()

        # Colgroup
        for element in soup.findAll('colgroup'):
            if element.attr is None:
                is_empty = True
                for child in element.children:
                    if child.name == 'col':
                        is_empty = False
                if is_empty:
                    element.decompose()

        # Table Heads
        for element in soup.findAll('td'):
            for paragraph in element.findAll('p', class_=['Heading-2', 'table-heads-bold', 'table-heads-italic', 'timeline-table']):
                paragraph.unwrap()
                element.name = 'th'
        if re.sub(r'.*/', '', input_filename) == 'a-Welch.html':
            clean_paragraphs(['table-heads-italic'], None, 'italics')
        delete_class(soup, 'p', 'timeline-columns')
        clean_paragraphs(['table-heads-bold','tables_table-heads-bold'], None, 'bold')

        # Table Rows
        for element in soup.findAll('tr', class_=['No-Table-Style', '_idGenTableRowColumn-3', '_idGenTableRowColumn-12','Table-Heading-Style','Table-Style-1 ']):
            del element['class']

        # # Table Data (Cell)
        # for element in soup.findAll('td', class_='No-Table-Style'):
        #     del element['class']

        # Table Text
        clean_paragraphs(['table-text', '•table-text','tables_table-text','bold'], None, 'table-text')

        # Book Notices
        delete_class(soup, 'p', 'pub-info')
        delete_class(soup, 'p', 'book-title')

        # Infobox (a.k.a. "Sidebars")
        clean_paragraphs(['sidebar-title'], None, 'infobox-title')
        for title in soup.findAll('p', class_='infobox-title'):
            string = remove_line_breaks(str(title))
            new_title = BeautifulSoup(string, features='html.parser')
            title.replace_with(new_title)
        clean_paragraphs(['sidebar-heading'], None, 'infobox-heading')
        clean_paragraphs(['sidebar-subhead'], None, 'infobox-subheading')
        clean_paragraphs(['sidebar-no-indent'], None, 'indent-0-1')

        # Interview Transcriptions
        clean_paragraphs(['interview1'], None, 'interview-first')
        clean_paragraphs(['interview2','interview-subsequent'], None, 'interview-additional')

        # Dingbats
        clean_paragraphs(['dingbat-line'], None, 'dingbat')


        # Add on styling for dingbat
        for element in soup.findAll('p', class_="dingbat"):
            element['style'] = 'text-align: center;'

        # Remove <strong> tag if a children of <h1> <h2> <h3> or <h4>
        for element in soup.findAll('h1'):
            for tag in element('strong'):
                tag.unwrap()
        for element in soup.findAll('h2'):
            for tag in element('strong'):
                tag.unwrap()
        for element in soup.findAll('h3'):
            for tag in element('strong'):
                tag.unwrap()
        for element in soup.findAll('h4'):
            for tag in element('strong'):
                tag.unwap()

        # Delete Unnecessary Tags
        unwrap_element(soup, 'span', '_idGenDropcap-1')
        unwrap_element(soup, 'span', '_idGenCharOverride-1')
        unwrap_element(soup, 'div', '_idGenObjectStyleOverride-1')
        unwrap_element(soup, 'div', '_idGenObjectStyleOverride-2')
        unwrap_element(soup, 'div', '_idGenObjectStyleOverride-3')
        unwrap_element(soup, 'div', 'Basic-Text-Frame')
        unwrap_element(soup, 'span', 'Annotation-reference')
        unwrap_element(soup, 'div', '_idGenObjectLayout-1')
        unwrap_element(soup, 'div', '_idGenObjectLayout-3')
        unwrap_element(soup, 'div', '_idGenObjectLayout-4')
        unwrap_element(soup, 'div', '_idGenObjectLayout-5')
        unwrap_element(soup, 'div', '_idGenObjectAttribute-14')
        unwrap_element(soup, 'div', '_idGenObjectAttribute-18')
        unwrap_element(soup, 'span', 'reference-text')
        unwrap_element(soup, 'span', 'apple-converted-space')
        unwrap_element(soup, 'span', 'lining-numbers')
        unwrap_element(soup, 'span', 'roman')
        unwrap_element(soup, 'span', 'dates')
        unwrap_element(soup, 'span', 'featurestext')
        unwrap_element(soup, 'span', 'hollow')
        unwrap_element(soup, 'span', 'Zapf')

        delete_element(soup, 'p', '•Side-vertical-title')
        delete_element(soup, 'p', '•Book-Review-Sidebar')
        delete_element(soup, 'div', 'arrow')
        delete_element(soup, 'span', 'Endnote-Reference-no-super')


        remove_class(soup, 'p', 'ParaOverride-1')
        remove_class(soup, 'p', 'ParaOverride-2')
        remove_class(soup, 'p', 'ParaOverride-3')
        remove_class(soup, 'p', 'ParaOverride-4')
        remove_class(soup, 'p', 'ParaOverride-5')


        remove_class(soup, 'span', 'CharOverride-1')
        remove_class(soup, 'span', 'CharOverride-2')
        remove_class(soup, 'span', 'CharOverride-3')
        remove_class(soup, 'span', 'CharOverride-4')
        unwrap_element(soup, 'span', 'CharOverride-5')
        unwrap_element(soup, 'span', 'CharOverride-6')
        unwrap_element(soup, 'span', 'CharOverride-7')
        unwrap_element(soup, 'span', 'CharOverride-8')
        unwrap_element(soup, 'span', 'CharOverride-9')
        unwrap_element(soup, 'span', 'CharOverride-10')
        unwrap_element(soup, 'span', 'CharOverride-11')
        unwrap_element(soup, 'span', 'CharOverride-12')
        unwrap_element(soup, 'span', 'CharOverride-13')
        unwrap_element(soup, 'span', 'CharOverride-14')

        for element in soup.findAll('span', class_=""):
            element.unwrap()

    # Remove Unnecessary Container IDs and Generic Object Attributes
        for element in soup.findAll('div'):
            if element.get('id') is not None and re.match(r'_idContainer[0-9]{3}', element.get('id')):
                del element['id']
            if element.get('class') is not None and type(element.get('class')) == list \
                    and re.match(r'_idGenObjectAttribute-[0-9]{1,2}', element.get('class')[0]):
                del element['class']
            # Remove Empty Divs
            if element.get('id') is None and element.get('class') is None:
                element.unwrap()

        # create list of classes that we approve of
        known_classes = ['author', 'author-bio', 'subtitle', 'publication-info', 'author-book-notice', 'document-title',
                         'poetry-author']

        # inline text classes
        known_classes += ['superscript', 'strikethrough', 'italics', 'underline', 'small-caps', 'bold', 'hebrew',
                          'foreign', 'subscript']

        # horizontal spacing classes
        known_classes += ['indent-1-0', 'indent-0-1', 'indent-1-2', 'indent-2-0', 'indent-2-3', 'indent-3-4',
                          'indent-4-5', 'indent-2-2', 'indent-3-3', 'block-quote', 'block-quote-indent',
                          'publication-lines', 'right', 'interview-first', 'interview-additional', 'indent']

        # vertical spacing classes
        known_classes += ['begin', 'end', 'dingbat', 'poem-text']

        # footnote/appendix classes
        known_classes += ['footnote-link', 'footnote-body', 'all-footnotes', 'bibliography-entry', 'appendix-title', 'Masthead-Titles', 'Masthead-people']

        # image-related classes
        known_classes += ['graphic-frame', 'graphic-frame-outer', 'caption', 'caption-frame', 'invisible',
                          'inline-graphic']

        # author abstract classes
        known_classes += ['author-abstract', 'author-abstract-title', 'author-abstract-body']
        # table classes
        known_classes += ['table-head', 'table-text']
        # infobox classes
        known_classes += ['infobox-title', 'infobox-heading', 'infobox-subheading']

        # create a set of classes that we do not approve of
        unknown_classes = set()

        # loop through all tags to check that we approve all CSS classes in the file
        for element in soup.findAll(True):
            class_list = element.get('class')
            if class_list is not None:
                if type(element.get('class')) == str:
                    class_list = class_list.split()
                for class_name in class_list:
                    if class_name not in known_classes:
                        unknown_classes.add(class_name)

        # display warning if there are any unhandled classes
        for name in unknown_classes:
            filename = re.sub(r'.*/', '/', input_filename)
            print('\tUnrecognized Class Warning: ' + name + ' found in ' + filename)

        # save output to file
        if len(unknown_classes) == 0:
            with open(output_filename_clean, 'w', encoding='utf-8') as outfile:
                outfile.write(str(soup))
        else:
            with open(output_filename_partially_clean, 'w', encoding='utf-8') as outfile:
                outfile.write(str(soup))

def clean_batch(raw_files_path):

    # get the base path (the folder containing the folder with the raw html files)
    base_path = '/'.join(raw_files_path.split('/')[:-1])

    # get the files in the base directory
    if base_path == '':
        files = os.listdir()
    else:
        files = os.listdir(base_path)

    # if a folder for clean html files does not exist, create one
    clean_folder = 'clean_html_files'
    clean_files_path = base_path + '/' + clean_folder
    if clean_folder not in files:
        os.mkdir(clean_files_path)

    # if a folder for semi-clean html files does not exist, create one
    partially_clean_folder = 'semi-clean_html_files'
    partially_clean_files_path = base_path + '/' + partially_clean_folder
    if partially_clean_folder not in files:
        os.mkdir(partially_clean_files_path)

    # for each raw html file
    raw_files = os.listdir(raw_files_path)
    for file in raw_files:

        if file[:7] == 'Studyan':
            continue

        if file[-10:] == 'cover.html':
            continue

        if file[:7] == 'Front-M':
            continue

        print('Cleaning ' + file)
        clean_html_file(raw_files_path + '/' + file,
                        clean_files_path + '/' + file,
                        partially_clean_files_path + '/' + file)

    semiclean_files = os.listdir(partially_clean_files_path)
    if semiclean_files == ([]):
        os.rmdir(partially_clean_files_path)


# have the user select a directory
#tkinter.Tk().withdraw()
filename = askdirectory()
print('Extracting files from ' + filename)

# clean all the files in the selected directory
clean_batch(filename)
