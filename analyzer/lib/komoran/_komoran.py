import jpype
import os


class Komoran:
    def __init__(self, model_path='./komoran/models',
                 library_directory = './komoran/libs', max_memory=1024):
        
        libraries = [
            '{}/aho-corasick.jar',
            '{}/shineware-common-1.0.jar',
            '{}/shineware-ds-1.0.jar',
            '{}/komoran-3.0.jar'
        ]
        
        classpath = os.pathsep.join([lib.format(library_directory) for lib in libraries])
        jvmpath = jpype.getDefaultJVMPath()
        
        try:
            jpype.startJVM(
                jvmpath,
                '-Djava.class.path=%s' % classpath,
                '-Dfile.encoding=UTF8',
                '-ea', '-Xmx{}m'.format(max_memory)
            )
        except Exception as e:
            print(e)
    
        package = jpype.JPackage('kr.co.shineware.nlp.komoran.core')
        #help(package.Komoran.analyze.getTokenList)
        self.komoran = package.Komoran(model_path)        
        
    def set_user_dictionary(self, path):
        self.komoran.setUserDic(path)
    
    def pos(self, sent):
        tokens = self.komoran.analyze(sent).getTokenList()        
        tokens = [(token.getMorph(), token.getPos()) for token in tokens]
        return tokens
    
    def nouns(self, sent):
        return [noun for noun in self.komoran.analyze(sent).getNouns()]



        
