a = {'plan':
     {'custSegs':
          {'consumer': [
              {
                  'education': ['bbab5ef4-bbd3-44aa-a879-1a792a5feada', '4718bb8b-3018-4408-9ff1-68ab9c4f2b87'],
                  'gender': ['a9677a24-bc3c-40aa-8265-4be52545113b'],
                  'income': ['bdb6d057-80b7-411a-a6b6-12aae71581c3']
               }],
            'business': [
                {'company_size': ['37634235-3b04-4aad-a647-6d79a2c88655',
                                  'bbc364e1-2394-48c7-8aaf-774ba76942b6']
                 }]
          }
     }
}
import json
with open("example_response.json", "w") as conn:
    json.dump(a, conn)