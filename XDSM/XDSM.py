"""
XDSM tex source writer utility. Three methods:
1. addComp(name, style, string, stack=False)
      name: [string] label of the component
      style: [string] Tikz block style, defined in diagram_styles.tex
      string: [string] name of the component that appears in the pdf
      stack: [boolean] adds the stack option
2. addDep(out, inp, style, string, stack=False)
      out: [string] label of the component that depends on the variable
      inp: [string] label of the component that computes the variable
      style: [string] Tikz block style, defined in diagram_styles.tex
      string: [string] name of the variable that appears in the pdf
      stack: [boolean] adds the stack option
3. write(filename, compilepdf=False)
      filename: [string] write to filename+'.pdf'
      compilepdf: [string] whether to run pdflatex on the tex file
4. addChain( chain_node_list)
    list the chain in consequence

XDSMCJK
    add Chinese supporting using xetex and xeCJK package
    the interface is the same as XDSM
    the  characters in latex file need using UTF-8 encoding
    except ANSI characters

Original author:
    A.B.Labme lambe@utias.utoronto.ca
Modified By:
    David Chen greatcwmine@gmail.com

"""


class XDSM(object):

    """ original XDSM graphic class """

    def __init__(self, xdsm_path=None):
        """
        xdsm_path : the XDSM tex style file directory path,
                default is path of the same folder of XDSM.py """
        self.inds = {}
        self.comps = []
        self.deps = []
        self.chains = []

        if xdsm_path:
            self._xdsm_path = xdsm_path
        else:
            import os
            self._xdsm_path = os.path.dirname(os.path.abspath(__file__))

    def _is_empty_comp(self, name):
        """ define empty node rule """
        if name[:5] == 'EMPTY':
            return True
        else:
            return False

    def addComp(self, name, style, string, stack=False):
        """ addComp(name, style, string, stack=False)
            name: [string] label of the component
                    using EMPTY heading keywort to specify EMPTY node
                    (e.g. overall inputs and outpus)
            style: [string] Tikz block style, defined in diagram_styles.tex
            string: [string] name of the component that appears in the pdf
            stack: [boolean] adds the stack option
        """
        self.inds[name] = len(self.comps)
        self.comps.append([name, style, string, stack])

    def addDep(self, out, inp, style, string, stack=False):
        """ addDep(out, inp, style, string, stack=False)
            out: [string] label of the component that depends on the variable
            inp: [string] label of the component that computes the variable
            style: [string] Tikz block style, defined in diagram_styles.tex
            string: [string] name of the variable that appears in the pdf
            stack: [boolean] adds the stack option
        """

        self.deps.append([out, inp, style, string, stack])

    def addChain(self, chain_list):
        """ set the process chain list """
        if len(chain_list) < 2:
            raise ValueError('the process chain has 2 elements at least')
        self.chains.append(chain_list)

    def getCmds(self):
        """ generate the XDSM matrix node"""
        def write(i, j, name, style, string, stack):
            M[i][j] = '    \\node'
            M[i][j] += ' [' + style + (',stack]' if stack else ']')
            M[i][j] += ' (' + name + ')'
            M[i][j] += ' {' + string + '};'
            M[i][j] += ' &\n' if j < n - 1 \
                else (' \\\\\n    %Row ' + str(i+2) + '\n')

        n = len(self.comps)

        inds = self.inds

        names = [[None for j in range(n)]
                 for i in range(n)]

        for name, style, string, stack in self.comps:
            names[inds[name]][inds[name]] = name
        for out, inp, style, string, stack in self.deps:
            names[inds[inp]][inds[out]] = out+'-'+inp

        M = [
            [('    &\n' if j < n - 1 else '    \\\\\n') for j in range(n)]
            for i in range(n)]
        for name, style, string, stack in self.comps:
            # skip EMPTY* component
            if not self._is_empty_comp(name):
                write(inds[name], inds[name], name, style, string, stack)

        for out, inp, style, string, stack in self.deps:
            write(inds[inp], inds[out], out+'-'+inp, style, string, stack)

        H = ['' for i in range(n)]
        for i in range(n):
            minj = i
            maxj = i
            for out, inp, style, string, stack in self.deps:
                j = inds[out]
                if inds[inp] is i and not self._is_empty_comp(inp):
                    minj = j if j < minj else minj
                    maxj = j if j > maxj else maxj
            if minj is not maxj:
                H[i] = '   '
                H[i] += ' (' + names[i][minj] + ')'
                H[i] += ' edge [DataLine]'
                H[i] += ' (' + names[i][maxj] + ')\n'

        V = ['' for jj in range(n)]
        for j in range(n):
            mini = j
            maxi = j
            for out, inp, style, string, stack in self.deps:
                i = inds[inp]
                if inds[out] is j and not self._is_empty_comp(out):
                    mini = i if i < mini else mini
                    maxi = i if i > maxi else maxi
            if mini is not maxi:
                V[j] = '   '
                V[j] += ' (' + names[mini][j] + ')'
                V[j] += ' edge [DataLine]'
                V[j] += ' (' + names[maxi][j] + ')\n'

        return M, H, V

    def _write_construction(self, fun_w):
        """ write the XDSM construction code
        Args:
            fun_w: closure function fun_w(string) to write string to stream
        Return: None
        """
        n = len(self.comps)
        M, H, V = self.getCmds()
        w = lambda s: fun_w(s+'\n')
        import os
        xpath = self._xdsm_path.replace('\\', r'/')

        w('\\usepackage{geometry}')
        w('\\usepackage{amsfonts}')
        w('\\usepackage{amsmath}')
        w('\\usepackage{amssymb}')
        w('\\usepackage{tikz}')
        w('')
        w('\\input{%s/diagram_border}' % xpath)
        w('')
        w('\\begin{document}')
        w('')
        w('\\input{%s/diagram_styles}' % xpath)
        w('')
        w('\\begin{tikzpicture}')
        w('')

        w('  \\matrix[MatrixSetup]')
        w('  {')
        w('    %Row 1')
        for i in range(n):
            for j in range(n):
                fun_w(M[i][j])
        w('  };')
        w('')
        # for the chain process
        if self.chains:
            w(r'   % XDSM process chains ')
            for i, chn in enumerate(self.chains):
                w(r'   { [start chain=process]')
                w(r'       \begin{pgfonlayer}{process}')
                w(r'       \chainin (%s);' % chn[0])
                last_node = chn[0]
                for e in chn[1:]:
                    if '-' in e or '-' in last_node:
                        w(r'       \chainin (%s)    [join=by ProcessTip];' % e)
                    else:
                        w(r'       \chainin (%s)    [join=by ProcessHV];' % e)

                    last_node = e
                w(r'       \end{pgfonlayer}')
                w(r'   }')
                w('')

        w('  \\begin{pgfonlayer}{data}')
        w('    \\path')
        w('    % Horizontal edges')
        for i in range(n):
            fun_w(H[i])
        w('    % Vertical edges')
        for j in range(n):
            fun_w(V[j])
        w('    ;')
        w('  \\end{pgfonlayer}')

        w('')
        w('\\end{tikzpicture}')
        w('')
        w('\\end{document}')

    def write(self, filename, compilepdf=False):
        """ generate latex  code """

        f = open(filename+'.tex', 'w')
        w = lambda s: f.write(s+'\n')

        w('\\documentclass{article}')

        self._write_construction(f.write)

        f.close()

        if compilepdf:
            self.compilepdf(filename)

    def compilepdf(self, filename):
        """ make using pdflatex to compile the tex file"""
        import os
        os.system('pdflatex ' + filename + '.tex')


class XDSMCJK(XDSM):

    """ XDSM class with Chinese based on xetex and xeCJK package"""

    def write(self, filename, compilepdf=False):
        """ generate xatex  code """
        import codecs
        w = lambda s: f.write(s+'\n')
        f = codecs.open(filename+'.tex', 'w', 'utf-8')

        w(r'%# -*- coding:utf-8 -*-')
        w('\\documentclass{article}')
        w('\\usepackage{xeCJK}')
        w('\\setCJKmainfont{SimSun}')
        w('\\setmainfont{Times New Roman}')

        self._write_construction(f.write)

        f.close()

        if compilepdf:
            self.compilepdf(filename)

    def compilepdf(self, filename):
        filename = filename.strip()
        if filename[-3:] == '.tex':
            filename = filename[:-3]
        import os
        cmd = 'xelatex ' + filename + '.tex'
        dirname = os.path.dirname(filename)
        if dirname:
            cmd += ' -output-directory="%s"' % dirname
        ret = os.system(cmd)
        # open it to preview
        if ret == 0:
            if os.name == 'posix':  # *nix
                os.system('xdg-open' + filename + '.pdf')
            elif os.name == 'nt':  # windows
                os.system(filename.replace('/', '\\') + '.pdf')
