# analyzer
ngram_analyzer = 'ngram_analyzer'
edge_ngram_analyzer = 'edge_ngram_analyzer'
standard_analyzer = 'standard_analyzer'
phone_analyzer = 'phone_analyzer'
socials_analyzer = 'socials_analyzer'
email_analyzer = 'email_analyzer'
email_search_analyzer = 'email_search_analyzer'

analysis = {
    'filter': {
        'edge_ngram_filter': {
            'type': 'edgeNGram',
            'min_gram': 3,
            'max_gram': 20
        },
        'ngram_filter': {
            'type': 'nGram',
            'min_gram': 3,
            'max_gram': 20
        }
    },
    'char_filter': {
        'yo_char_filter': {
            'type': 'pattern_replace',
            'pattern': 'ё',
            'replacement': 'е'
        },
        'phone_char_filter': {
            'type': 'pattern_replace',
            'pattern': '\(|\)|\-|\+7|^7|^8',
            'replacement': ''
        },
        'email_char_filter': {
            'type': 'pattern_replace',
            'pattern': '@',
            'replacement': ''
        },
        'socials_char_filter': {
            'type': 'pattern_replace',
            'pattern': '\(|\)',
            'replacement': ''
        },
    },
    'analyzer': {
        ngram_analyzer: {
            'type': 'custom',
            'char_filter': ['yo_char_filter'],
            'tokenizer': 'standard',
            'filter': [
                'lowercase',
                'ngram_filter'
            ]
        },
        edge_ngram_analyzer: {
            'type': 'custom',
            'char_filter': ['yo_char_filter'],
            'tokenizer': 'standard',
            'filter': [
                'lowercase',
                'edge_ngram_filter'
            ]
        },
        standard_analyzer: {
            'type': 'custom',
            'char_filter': ['yo_char_filter'],
            'tokenizer': 'standard',
            'filter': [
                'lowercase'
            ]
        },
        phone_analyzer: {
            'type': 'custom',
            'char_filter': ['phone_char_filter'],
            'tokenizer': 'keyword',
            'filter': [
                'lowercase'
            ]
        },
        socials_analyzer: {
            'type': 'custom',
            'tokenizer': 'keyword',
            'char_filter': ['socials_char_filter'],
            'filter': [
                'lowercase',
            ]
        },
        email_analyzer: {
            'type': 'custom',
            'tokenizer': 'uax_url_email',
            'filter': [
                'lowercase',
                'ngram_filter'
            ]
        },
        email_search_analyzer: {
            'type': 'custom',
            'tokenizer': 'uax_url_email',
            'filter': [
                'lowercase',
            ]
        }
    }
}
