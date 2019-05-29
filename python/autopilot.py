import platform
from chain.builtin import ProcessingChain
from settingstree import Settings


if __name__ == '__main__':
    ProcessingChain.get_platform_specific_chain().run()
