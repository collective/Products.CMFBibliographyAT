
from kss.plugin.livesearch.autocompleteview import AutoCompleteView

class AuthorListView(AutoCompleteView):

    data = [
        'hauser',
        'natea',
        'mateola',
        'jchamm',
        'ree',
        'ree_',
        'martior',
        'dcnoye',
        'jonstahl',
        'SteveM',
        'grahamperrin',
        'ErikRose',
        'heureso',
        'cbcunc',
        'enzo',
        'esteele',
        'geojeff',
        'wildintellect',
        'Gogo',
        'aclark',
        'zenwryly',
        'SnarfBot',
        'siebo',
        'siebo_',
        'DigitalD',
        'place',
        'plate',
        'plural',
        'plone',
        'apostle',
        'april',
        'apple',
        ]
    data.sort()

    def update(self, q, limit=10):
        
        # Acqire additional parameters.

        words = self.data
        print words

        # result is sorted already at this point.

        term = q.strip()

        self.results = results = []
        
        if not term:
            # Just do nothing if we just typed the comma.
            return

        for w in words:
            if w.lower().startswith(term.lower()):
                if len(results) < limit:
                    results.append(w)
                else:
                    # we are over the limit already, we don't add that
                    # but we swith on the "more" link if there is one.
                    self.showMore = True
                    break
