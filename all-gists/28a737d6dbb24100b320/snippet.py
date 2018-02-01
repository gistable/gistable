class Docstring(object):
    """
    Builds a docstring for functions/methods accoring to the numpy styleguide.

    The class can be used dynamically with the ``add_*`` functions or
    completly filled while creating an instance. For convenience use to get the
    docstring one can use the :meth:`Docstring.build` or by calling
    :func:`str` on an instance. Using a console also allows to simply call the
    :meth:`Docstring.__repr__`.

    Parameters
    ----------

    short_description : `str`, optional
        Short description of the functions function.

    long_description : `str`, optional
        Long descriptions of the functions function.

    params : `dict` or `list` / `tuple` of `dict`-s, optional
        The parameter specifications. The `dict` *should* contain the
        keywords ``name`` (the name of the parameter), ``typ`` (the typ
        of the parameter), ``description`` (the description for the
        parameters function) and may contain ``optional`` (`bool` if the
        parameter is optional) and ``default`` (the default value if the
        parameter is optional and not passed explicitly). All these
        keywords are converted to `str` except for ``optional``.

    returns : `dict` or `list` / `tuple` of `dict`-s, optional
        The returns parameters specifications. The `dict` should contain
        the keywords ``name``, ``typ`` and ``description`` which are `str` or
        convertable to `str`.

    raises : `dict` or `list` / `tuple` of `dict`-s, optional
        The raises exceptions or error specifications. The `dict` should
        contain the keywords ``exception`` and ``description`` which are
        `str` or convertable to `str`.

    sections : `dict` or `list` / `tuple` of `dict`-s, optional
        Additional sections. The `dict` should contain the keywords
        ``section_name`` and ``content`` which are `str` or convertable to
        `str`.

    Notes
    -----

    1. This class is not written for any specific documentation building module
       or program. So the given strings anywhere are taken literally.

    2. This class's primary focus is to ease documentation if some parameters
       are shared by several functions. So you can define at the start of the
       module which parameters are used and then build the documentation when
       importing the module. Or if some parameters are shared by several
       different modules one could create a seperate module that defines the
       descriptions.

    3. Since there a lot of string operations it may not be the best idea to
       use it too frequently if performance matters.

    4. The ``create_*`` functions are classmethods to allow creating a for
       example single parameter docstring without using the whole class. See
       :meth:`Docstring.create_parameter` or similar.

    5. If you want to add the docstrings to a function you can use the
       :func:`add_docstring` as decorator.

    Examples
    --------

    Building it dynamically::

        >>> doc = Docstring()
        >>> doc.add_short_description('This is the short description.')
        >>> doc.add_long_description('This is the long description.')
        >>> doc # doctest: +SKIP
        <BLANKLINE>
        This is the short description.
        <BLANKLINE>
        This is the long description.
        >>> param = {'name': 'number', 'typ': '`int`',
        ...          'description': 'The number to use.'}
        >>> doc.add_params(param)
        >>> doc # doctest: +SKIP
        This is the short description.
        <BLANKLINE>
        This is the long description.
        <BLANKLINE>
        Parameters
        ----------
        <BLANKLINE>
        number : `int`
            The number to use.
        >>> param1 = {'name': 'number2', 'typ': '`int`',
        ...           'description': 'The other number to use.'}
        >>> param2 = {'name': 'number3', 'typ': '`int`',
        ...           'description': 'The other other number to use.',
        ...           'optional':True, 'default':'0'}
        >>> params = [param1, param2]
        >>> doc.add_params(params)
        >>> doc # doctest: +SKIP
        This is the short description.
        <BLANKLINE>
        This is the long description.
        <BLANKLINE>
        Parameters
        ----------
        <BLANKLINE>
        number : `int`
            The number to use.
        <BLANKLINE>
        number2 : `int`
            The other number to use.
        <BLANKLINE>
        number3 : `int`, optional
            The other other number to use.
            Default is 0.
        >>> # Returns and Raises do work the same but take different keywords.
        >>> returns = {'name': 'result', 'typ': '`int`',
        ...            'description': 'Functions result with the three inputs'}
        >>> raises = {'name': 'ValueError',
        ...           'description': 'Not numerical input.'}
        >>> doc.add_returns(returns)
        >>> doc.add_raises(raises)
        >>> doc # doctest: +SKIP
        This is the short description.
        <BLANKLINE>
        This is the long description.
        <BLANKLINE>
        Parameters
        ----------
        <BLANKLINE>
        number : `int`
            The number to use.
        <BLANKLINE>
        number2 : `int`
            The other number to use.
        <BLANKLINE>
        number3 : `int`, optional
            The other other number to use.
            Default is 0.
        <BLANKLINE>
        Returns
        -------
        <BLANKLINE>
        result : `int`
            Functions result with the three inputs
        <BLANKLINE>
        Raises
        ------
        <BLANKLINE>
        ValueError :
            Not numerical input.
        >>> section1 = {'name': 'Notes', 'content': 'These are the Notes'}
        >>> section2 = {'name': 'Examples',
        ...             'content': 'These are the examples'}
        >>> sections = [section1, section2]
        >>> doc.add_sections(sections)
        >>> doc # doctest: +SKIP
        This is the short description.
        <BLANKLINE>
        This is the long description.
        <BLANKLINE>
        Parameters
        ----------
        <BLANKLINE>
        number : `int`
            The number to use.
        <BLANKLINE>
        number2 : `int`
            The other number to use.
        <BLANKLINE>
        number3 : `int`, optional
            The other other number to use.
            Default is 0.
        <BLANKLINE>
        Returns
        -------
        <BLANKLINE>
        result : `int`
            Functions result with the three inputs
        <BLANKLINE>
        Raises
        ------
        <BLANKLINE>
        ValueError :
            Not numerical input.
        <BLANKLINE>
        Examples
        --------
        <BLANKLINE>
        These are the examples
        <BLANKLINE>

    The alternative is to create the ``Docstring`` already with these
    attributes::

        >>> doc2 = Docstring('This is the short description.',
        ...    'This is the long description.', [param, param1, param2],
        ...    returns, raises, sections)
        >>> doc2 # doctest: +SKIP
        This is the short description.
        <BLANKLINE>
        This is the long description.
        <BLANKLINE>
        Parameters
        ----------
        <BLANKLINE>
        number : `int`
            The number to use.
        <BLANKLINE>
        number2 : `int`
            The other number to use.
        <BLANKLINE>
        number3 : `int`, optional
            The other other number to use.
            Default is 0.
        <BLANKLINE>
        Returns
        -------
        <BLANKLINE>
        result : `int`
            Functions result with the three inputs
        <BLANKLINE>
        Raises
        ------
        <BLANKLINE>
        ValueError :
            Not numerical input.
        <BLANKLINE>
        Examples
        --------
        <BLANKLINE>
        These are the examples
        <BLANKLINE>

    """
    def __init__(self, short_description="", long_description="", params=None,
                 returns=None, raises=None, sections=None):
        self.short_description = str(short_description).strip()
        self.long_description = str(long_description).strip()
        self._parameter = []
        self._return = []
        self._raises = []
        self._sections = []
        if params is not None:
            self.add_params(params)
        if returns is not None:
            self.add_returns(returns)
        if raises is not None:
            self.add_raises(raises)
        if sections is not None:
            self.add_sections(sections)

    @classmethod
    def create_parameter(cls, name, typ=None, description=None,
                         optional=False, default=None):
        """
        Build a parameter docstring.

        Parameters
        ----------

        name : `str`
            The name of the parameter

        typ : `str`, optional
            the supposed type of the parameter.
            Default is ``None``.

        optional : `bool`, optional
            ``True`` if the parameter is optional, ``False`` if not.
            Default is ``False``.

        default : `str`, optional
            The default value for the parameter.
            Ignored if optional is ``False``.
            Default is ``None``.

        description : `str`, optional
            The parameter description.
            Default is ``None``.

        Returns
        -------

        param_docstring : `str`
            The docstring describing the parameter.

        Examples
        --------

            >>> param1 = {'name': 'number', 'typ': '`int`',
            ...           'description': 'The number used for operating.',
            ...           'optional':True, 'default':'0'}
            >>> print(Docstring.create_parameter(**param1)) # doctest: +SKIP
            number : `int`, optional
                The number used for operating.
                Default is 0.
        """
        # Process the name of the parameter
        if name is None:
            return ''
        else:
            name = str(name).strip()

        # Process the type of the parameter
        if typ is None:
            typ = 'undefined'
        else:
            typ = str(typ).strip()

        # Process optional and default of the parameter
        if optional:
            optional = ', optional'
            if default is None:
                default = '\n    *No default is specified.*'
            else:
                default = '\n    Default is {default}.'.format(
                                            default=str(default).strip())
        else:
            optional = ''
            default = ''

        # Process the description of the parameter
        if description is None:
            description = '    *No description is provided.*'
        else:
            description = '    ' + str(description).strip()

        return """{name} : {typ}{opt}\n{desc}{default}""".format(name=name,
                      typ=typ, opt=optional, desc=description, default=default)

    @classmethod
    def create_return(cls, name, typ=None, description=None):
        """
        Build a return variable docstring.

        Parameters
        ----------

        name : `str`
            The name of the return variable

        typ : `str`, optional
            the supposed type of the return variable.
            Default is ``None``.

        description : `str`, optional
            The return variable description.
            Default is ``None``.

        Returns
        -------

        return_docstring : `str`
            The docstring describing the returned variable.

        Examples
        --------

            >>> return1 = {'name': 'number', 'typ': '`int`',
            ...            'description': 'The resulting number.'}
            >>> print(Docstring.create_return(**return1)) # doctest: +SKIP
            number : `int`
                The resulting number.
        """
        # Process the name of the return
        if name is None:
            return ''
        else:
            name = str(name).strip()

        # Process the type of the return
        if typ is None:
            typ = 'undefined'
        else:
            typ = str(typ).strip()

        # Process the description of the return
        if description is None:
            description = '    *No description is provided.*'
        else:
            description = '    ' + str(description).strip()

        return """{name} : {typ}\n{desc}""".format(name=name, typ=typ,
                                                   desc=description)

    @classmethod
    def create_raises(cls, name, description=None):
        """
        Build a raises exception docstring.

        Parameters
        ----------

        name : `str`
            The name of the type of exception

        description : `str`, optional
            The description explaining when the exception is raised.
            Default is ``None``.

        Returns
        -------

        raises_docstring : `str`
            The docstring describing the exception.

        Examples
        --------

            >>> raises1 = {'name': 'ValueError',
            ...           'description': 'Non-numerical input.'}
            >>> print(Docstring.create_raises(**raises1)) # doctest: +SKIP
            ValueError :
                Non-numerical input.
        """
        # Process the name of the raises
        if name is None:
            return ''
        else:
            exception = str(name).strip()

        # Process the description of the raises
        if description is None:
            description = '    *No description is provided.*'
        else:
            description = '    ' + str(description).strip()

        return """{name} :\n{desc}""".format(name=exception,
                                             desc=description)

    @classmethod
    def create_headline(cls, section_name):
        """
        Creates an underlining for a section name.

        Parameters
        ----------

        section_name : `str`
            The name of the section

        Returns
        -------

        section_headline : `str`
            The headline for this section.

        Examples
        --------

            >>> header1 = {'section_name': 'Notes'}
            >>> print(Docstring.create_headline(**header1)) # doctest: +SKIP
            Notes
            -----
        """
        section_name = str(section_name).strip()
        underline = '-' * len(section_name)
        return """{name}\n{line}""".format(name=section_name, line=underline)

    @classmethod
    def create_section(cls, name, content):
        """
        Combines the headline of a section with the content.

        Parameters
        ----------

        name : `str`
            The name of the section.

        content : `str`
            The content of the section.

        Returns
        -------
        section_docstring : `str`
            The docstring describing the section.

        Examples
        --------

            >>> section1 = {'name': 'Examples',
            ...            'content': 'These are the examples.'}
            >>> print(Docstring.create_section(**section1)) # doctest: +SKIP
            Examples
            --------
            <BLANKLINE>
            These are the examples.
        """
        headline = cls.create_headline(name)
        content = str(content).strip()
        return "{name}\n\n{content}".format(name=headline, content=content)

    def add_short_description(self, short_description):
        """
        Replace the short description.

        Parameters
        ----------

        short_description : `str`, optional
            Short description of the functions function.
        """
        self.short_description = str(short_description)

    def add_long_description(self, long_description):
        """
        Replace the long description.

        Parameters
        ----------

        long_description : `str`, optional
            Long description of the functions function.
        """
        self.long_description = str(long_description)

    def add_params(self, params):
        """
        Add another set of parameters to the list of parameters

        Parameters
        ----------

        params : `dict` or `list` / `tuple` of `dict`-s
            The parameter specifications. The `dict` *should* contain the
            keywords ``name`` (the name of the parameter), ``typ`` (the typ
            of the parameter), ``description`` (the description for the
            parameters function) and may contain ``optional`` (`bool` if the
            parameter is optional) and ``default`` (the default value if the
            parameter is optional and not passed explicitly). All these
            keywords are converted to `str` except for ``optional``.
        """
        if isinstance(params, dict):
            self._parameter.append(params)
        elif isinstance(params, (list, tuple)):
            for i in params:
                self.add_params(i)

    def add_returns(self, returns):
        """
        Add another set of returned parameters to the list of returns

        Parameters
        ----------
        returns : `dict` or `list` / `tuple` of `dict`-s, optional
            The returns parameters specifications. The `dict` should contain
            the keywords ``name``, ``typ`` and ``description`` which are `str`
            or convertable to `str`.
        """
        if isinstance(returns, dict):
            self._return.append(returns)
        elif isinstance(returns, (list, tuple)):
            for i in returns:
                self.add_returns(i)

    def add_raises(self, raises):
        """
        Add another set of raises to the list of raises

        Parameters
        ----------

        raises : `dict` or `list` / `tuple` of `dict`-s, optional
            The raises exceptions or error specifications. The `dict` should
            contain the keywords ``exception`` and ``description`` which are
            `str` or convertable to `str`.
        """
        if isinstance(raises, dict):
            self._raises.append(raises)
        elif isinstance(raises, (list, tuple)):
            for i in raises:
                self.add_raises(i)

    def add_sections(self, sections):
        """
        Add another set of sections to the list of sections

        Parameters
        ----------
        sections : `dict` or `list` / `tuple` of `dict`-s, optional
            Additional sections. The `dict` should contain the keywords
            ``section_name`` and ``content`` which are `str` or convertable to
            `str`.
        """
        if isinstance(sections, dict):
            self._sections.append(sections)
        elif isinstance(sections, (list, tuple)):
            for i in sections:
                self.add_sections(i)

    def build(self):
        """
        Builds the complete docstring.

        Returns
        -------
        docstring: `str`
            The complete docstring.
        """
        docstring = []
        if self.short_description:
            docstring.append(self.short_description)
            if self.long_description:
                docstring.append(self.long_description)
        if self._parameter:
            params = []
            for i in self._parameter:
                params.append(self.create_parameter(**i))
            params = '\n\n'.join(params)
            docstring.append(self.create_section('Parameters', params))
        if self._return:
            returns = []
            for i in self._return:
                returns.append(self.create_return(**i))
            returns = '\n\n'.join(returns)
            docstring.append(self.create_section('Returns', returns))
        if self._raises:
            raises = []
            for i in self._raises:
                raises.append(self.create_raises(**i))
            raises = '\n\n'.join(raises)
            docstring.append(self.create_section('Raises', raises))
        if self._sections:
            for i in self._sections:
                docstring.append(self.create_section(**i))
        return '\n\n'.join(docstring)

    def __str__(self):
        return self.build()

    def __repr__(self):
        return self.build()


def add_docstring(docstring, replace=True):
    """
    Useable for replacing a docstring on a function or method or appending
    to it.

    This decorator keeps the functions signature and only alters the docstring.
    The primary use-case would be if multiple functions have the same or only
    a slightly different *long* docstring and you want to DRY
    (https://de.wikipedia.org/wiki/Don%E2%80%99t_repeat_yourself).

    Parameters
    ----------
    docstring: `str`
        The docstring that will be appended or set for the function/method

    replace: `bool`
        If ``True`` the original docstring is replaced and if ``False`` the
        new docstring is added to the original docstring. Default is ``True``

    Notes
    -----
    Using this decorator allows Sphinx and the spyder object inspector load the
    new docstring.

    For example::

        >>> from astropy.utils.decorators import add_docstring
        >>> doc = '''Perform num1 {op} num2'''
        >>> @add_docstring(doc.format(op='+'))
        ... def add(num1, num2):
        ...     return num1+num2
        ...
        >>> help(add) # doctest: +SKIP
        Help on function add in module __main__:
        add(num1, num2)
            Perform num1 + num2

    sometimes only appending some common docstring is required. In that case
    setting ``replace`` to ``False`` will only append the docstring.

        >>> doc = '''
        ...       Parameters
        ...       ----------
        ...       num1, num2 : Numbers
        ...       Returns
        ...       -------
        ...       result: Number
        ...       '''
        >>> @add_docstring(doc, replace=False)
        ... def add(num1, num2):
        ...     '''Perform addition.'''
        ...     return num1+num2
        ...
        >>> help(add) # doctest: +SKIP
        Help on function add in module __main__:
        add(num1, num2)
            Perform addition
            Parameters
            ----------
            num1, num2 : Numbers
            Returns
            -------
            result: Number
    """
    def set_docstring(func):
        if replace:
            func.__doc__ = docstring
        else:
            func.__doc__ = func.__doc__ + docstring
        return func
    return set_docstring
