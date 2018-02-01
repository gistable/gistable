#!/usr/bin/env python
#
# Copyright (C) 2013 Stanislav Golovanov <stgolovanov@gmail.com>
#                    Strahinja Val Markovic  <val@markovic.io>
#
# This file is part of YouCompleteMe.
#
# YouCompleteMe is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# YouCompleteMe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with YouCompleteMe.  If not, see <http://www.gnu.org/licenses/>.

from ycm.completers.general_completer import GeneralCompleter
import vim


class NeoSnippetCompleter( GeneralCompleter ):
  """
  General completer that provides UltiSnips snippet names in completions.
  """

  def __init__( self ):
    super( NeoSnippetCompleter, self ).__init__()
    self._candidates = None
    self._filtered_candidates = None


  def ShouldUseNowInner( self, start_column ):
    return self.QueryLengthAboveMinThreshold( start_column )


  def CandidatesForQueryAsync( self, query, unused_start_column ):
    self._filtered_candidates = self.FilterAndSortCandidates( self._candidates,
                                                              query )


  def AsyncCandidateRequestReady( self ):
    return True


  def CandidatesFromStoredRequest( self ):
    return self._filtered_candidates if self._filtered_candidates else []


  def OnBufferVisit( self ):
    self._candidates = _GetCandidates()


def _GetCandidates():
  try:
    neosnips = vim.eval('neosnippet#get_snippets()')

    return  [ { 'word': str( snip ),
                'menu': '<snip> ' + str( attr['menu_abbr'] )}
                for snip, attr in neosnips.items() ]
  except:
    return []