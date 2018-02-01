"""
Copyright (c) 2012-2014, Eventbrite and Contributors
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

Neither the name of Eventbrite nor the names of its contributors may
be used to endorse or promote products derived from this software
without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""


class EncodedString(str):
    """A string with a stored encoding.

    By storing the unicode encoding used, we're able to handle unicode decoding
    without falling back to the system default encoding. If constructed any way
    other than with the ``new`` class method, encoding is set to UTF-8.
    """

    encoding = 'utf8'

    @classmethod
    def new(cls, content, encoding='utf8', encode=True):
        """Create a new instance of EncodedString.

        Creates a new EncodedString instance with the given ``encoding``.
        ``content`` will be encoded before instantiation by default.  If
        ``content`` has already been encoded, pass ``False for the ``encode``
        keyword argument.
        """

        if encode:
            content = content.encode(encoding)
        result = cls(content)
        result.encoding = encoding

        return result

    def __add__(self, other):
        """Concatenate EncodedString with another object.

        If ``other`` is a Unicode object, the contents of ``self`` will be
        decoded. Otherwise a new EncodedString will be returned with the same
        encoding.
        """

        if isinstance(other, unicode):
            # decode and concatenate
            return u'%s%s' % (self, other)

        # return a new EncodedString keeping the same encoding
        return EncodedString.new(
            '%s%s' % (self, other),
            self.encoding,
            encode=False,
        )

    def __radd__(self, other):
        """Concatenate EncodedString with another object.

        If ``other`` is a Unicode object, the contents of ``self`` will be
        decoded. Otherwise a new EncodedString will be returned with the same
        encoding.
        """

        if isinstance(other, unicode):
            # decode and concatenate
            return u'%s%s' % (other, self)

        # return a new EncodedString keeping the same encoding
        return EncodedString.new(
            '%s%s' % (other, self),
            self.encoding,
            encode=False,
        )

    def __unicode__(self):
        """Return a unicode representation using the stored encoding."""

        return self.decode()

    def decode(self, *args):
        """Decode EncodedString contents to a Unicode object.

        If no encoding is specified, use the stored encoding.
        """

        # if args are omitted, use the stored encoding
        if len(args) == 0:
            args = [self.encoding]

        return str.decode(self, *args)
