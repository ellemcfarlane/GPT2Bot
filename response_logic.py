import gpt_2_simple as gpt2
"""
Functions to allow initialization of GTP-2 model for Twitter bot response
"""
# set GTP-2 model
model_name = "124M"
# initiate session
#gpt2.download_gpt2(model_name=model_name)
sess = gpt2.start_tf_sess()

def loadModel():
    # load model for generating response text
    gpt2.load_gpt2(sess, model_name=model_name)
    print("GPT2 model loaded.")

def getAnswer(prefix, length=45, temperature=.7, top_p=.9):
    # generate GTP-2 response with given prefix (text to "inspire" the GTP-2 AI)
    response = gpt2.generate(sess, return_as_list=True,
                              model_name=model_name,
                              prefix=prefix,
                              length=45,
                              temperature=0.7,
                              top_p=0.9,
                              include_prefix=True
                             )[0]
    return response





