# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\markdown\preprocessors.py
import re
import markdown.util as util
import odict

def build_preprocessors(md_instance, **kwargs):
    preprocessors = odict.OrderedDict()
    if md_instance.safeMode != 'escape':
        preprocessors['html_block'] = HtmlBlockPreprocessor(md_instance)
    preprocessors['reference'] = ReferencePreprocessor(md_instance)
    return preprocessors


class Preprocessor(util.Processor):

    def run(self, lines):
        pass


class HtmlBlockPreprocessor(Preprocessor):
    right_tag_patterns = ['</%s>', '%s>']
    attrs_pattern = '\n        \\s+(?P<attr>[^>"\'/= ]+)=(?P<q>[\'"])(?P<value>.*?)(?P=q)   # attr="value"\n        |                                                         # OR \n        \\s+(?P<attr1>[^>"\'/= ]+)=(?P<value1>[^> ]+)               # attr=value\n        |                                                         # OR\n        \\s+(?P<attr2>[^>"\'/= ]+)                                  # attr\n        '
    left_tag_pattern = '^\\<(?P<tag>[^> ]+)(?P<attrs>(%s)*)\\s*\\/?\\>?' % attrs_pattern
    attrs_re = re.compile(attrs_pattern, re.VERBOSE)
    left_tag_re = re.compile(left_tag_pattern, re.VERBOSE)
    markdown_in_raw = False

    def _get_left_tag(self, block):
        m = self.left_tag_re.match(block)
        if m:
            tag = m.group('tag')
            raw_attrs = m.group('attrs')
            attrs = {}
            if raw_attrs:
                for ma in self.attrs_re.finditer(raw_attrs):
                    if ma.group('attr'):
                        if ma.group('value'):
                            attrs[ma.group('attr').strip()] = ma.group('value')
                        else:
                            attrs[ma.group('attr').strip()] = ''
                    elif ma.group('attr1'):
                        if ma.group('value1'):
                            attrs[ma.group('attr1').strip()] = ma.group('value1')
                        else:
                            attrs[ma.group('attr1').strip()] = ''
                    elif ma.group('attr2'):
                        attrs[ma.group('attr2').strip()] = ''

            return (tag, len(m.group(0)), attrs)
        else:
            tag = block[1:].split('>', 1)[0].lower()
            return (tag, len(tag) + 2, {})

    def _recursive_tagfind(self, ltag, rtag, start_index, block):
        while 1:
            i = block.find(rtag, start_index)
            if i == -1:
                return -1
            j = block.find(ltag, start_index)
            if j > i or j == -1:
                return i + len(rtag)
            j = block.find('>', j)
            start_index = self._recursive_tagfind(ltag, rtag, j + 1, block)
            if start_index == -1:
                return -1

    def _get_right_tag(self, left_tag, left_index, block):
        for p in self.right_tag_patterns:
            tag = p % left_tag
            i = self._recursive_tagfind('<%s' % left_tag, tag, left_index, block)
            if i > 2:
                return (tag.lstrip('<').rstrip('>'), i)

        return (block.rstrip()[-left_index:-1].lower(), len(block))

    def _equal_tags(self, left_tag, right_tag):
        if left_tag[0] in ('?', '@', '%'):
            return True
        elif '/' + left_tag == right_tag:
            return True
        elif right_tag == '--' and left_tag == '--':
            return True
        elif left_tag == right_tag[1:] and right_tag[0] == '/':
            return True
        else:
            return False

    def _is_oneliner(self, tag):
        return tag in ('hr', 'hr/')

    def run(self, lines):
        text = '\n'.join(lines)
        new_blocks = []
        text = text.split('\n\n')
        items = []
        left_tag = ''
        right_tag = ''
        in_tag = False
        while text:
            block = text[0]
            if block.startswith('\n'):
                block = block[1:]
            text = text[1:]
            if block.startswith('\n'):
                block = block[1:]
            if not in_tag:
                if block.startswith('<') and len(block.strip()) > 1:
                    if block[1] == '!':
                        left_tag, left_index, attrs = '--', 2, {}
                    else:
                        left_tag, left_index, attrs = self._get_left_tag(block)
                    right_tag, data_index = self._get_right_tag(left_tag, left_index, block)
                    if data_index < len(block) and (util.isBlockLevel(left_tag) or left_tag == '--'):
                        text.insert(0, block[data_index:])
                        block = block[:data_index]
                    if not (util.isBlockLevel(left_tag) or block[1] in ('!', '?', '@', '%')):
                        new_blocks.append(block)
                        continue
                    if self._is_oneliner(left_tag):
                        new_blocks.append(block.strip())
                        continue
                    if block.rstrip().endswith('>') and self._equal_tags(left_tag, right_tag):
                        if self.markdown_in_raw and 'markdown' in attrs.keys():
                            start = re.sub('\\smarkdown(=[\\\'"]?[^> ]*[\\\'"]?)?', '', block[:left_index])
                            end = block[-len(right_tag) - 2:]
                            block = block[left_index:-len(right_tag) - 2]
                            new_blocks.append(self.markdown.htmlStash.store(start))
                            new_blocks.append(block)
                            new_blocks.append(self.markdown.htmlStash.store(end))
                        else:
                            new_blocks.append(self.markdown.htmlStash.store(block.strip()))
                        continue
                    else:
                        if util.isBlockLevel(left_tag) or left_tag == '--' and not block.rstrip().endswith('>'):
                            items.append(block.strip())
                            in_tag = True
                        else:
                            new_blocks.append(self.markdown.htmlStash.store(block.strip()))
                        continue
                new_blocks.append(block)
            else:
                items.append(block)
                right_tag, data_index = self._get_right_tag(left_tag, 0, block)
                if self._equal_tags(left_tag, right_tag):
                    if data_index < len(block):
                        items[-1] = block[:data_index]
                        text.insert(0, block[data_index:])
                    in_tag = False
                    if self.markdown_in_raw and 'markdown' in attrs.keys():
                        start = re.sub('\\smarkdown(=[\\\'"]?[^> ]*[\\\'"]?)?', '', items[0][:left_index])
                        items[0] = items[0][left_index:]
                        end = items[-1][-len(right_tag) - 2:]
                        items[-1] = items[-1][:-len(right_tag) - 2]
                        new_blocks.append(self.markdown.htmlStash.store(start))
                        new_blocks.extend(items)
                        new_blocks.append(self.markdown.htmlStash.store(end))
                    else:
                        new_blocks.append(self.markdown.htmlStash.store('\n\n'.join(items)))
                    items = []

        if items:
            if self.markdown_in_raw and 'markdown' in attrs.keys():
                start = re.sub('\\smarkdown(=[\\\'"]?[^> ]*[\\\'"]?)?', '', items[0][:left_index])
                items[0] = items[0][left_index:]
                end = items[-1][-len(right_tag) - 2:]
                items[-1] = items[-1][:-len(right_tag) - 2]
                new_blocks.append(self.markdown.htmlStash.store(start))
                new_blocks.extend(items)
                if end.strip():
                    new_blocks.append(self.markdown.htmlStash.store(end))
            else:
                new_blocks.append(self.markdown.htmlStash.store('\n\n'.join(items)))
            new_blocks.append('\n')
        new_text = '\n\n'.join(new_blocks)
        return new_text.split('\n')


class ReferencePreprocessor(Preprocessor):
    TITLE = '[ ]*(\\"(.*)\\"|\\\'(.*)\\\'|\\((.*)\\))[ ]*'
    RE = re.compile('^[ ]{0,3}\\[([^\\]]*)\\]:\\s*([^ ]*)[ ]*(%s)?$' % TITLE, re.DOTALL)
    TITLE_RE = re.compile('^%s$' % TITLE)

    def run(self, lines):
        new_text = []
        while lines:
            line = lines.pop(0)
            m = self.RE.match(line)
            if m:
                id = m.group(1).strip().lower()
                link = m.group(2).lstrip('<').rstrip('>')
                t = m.group(5) or m.group(6) or m.group(7)
                if not t:
                    tm = self.TITLE_RE.match(lines[0])
                    if tm:
                        lines.pop(0)
                        t = tm.group(2) or tm.group(3) or tm.group(4)
                self.markdown.references[id] = (link, t)
            else:
                new_text.append(line)

        return new_text