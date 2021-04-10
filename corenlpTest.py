from stanza.server import CoreNLPClient
client = CoreNLPClient(start_server=True)

#test1 = "cindy's book is red Sant'Eufemia Anglo-Saxon T(n) DTIME(f(n)) O(n2) color. the book cost US$1,000,000 NP-complete P ⊆ NP ⊆ PP ⊆ PSPACE Hospitality Business/Financial Centre."
test1 = "cindy bought book Anglo-Saxon from New York, the books looks quite good. Do you like this book?" 
'''
annotators=['tokenize','ssplit','pos','lemma','depparse','ner']+\
           ['natlog','openie']
'''
annotators=['tokenize','ssplit']
properties={
    'tokenize.whitespace': 'false', 
    'outputFormat': 'json'
}
output = client.annotate(text=test1, annotators=annotators, properties=properties)
print('output:', output)

for sentence in output['sentences']:
    origin = "" 
    for token in sentence['tokens']:
        origin = origin + token['before'] + token['originalText']
    print('origin:', origin)


