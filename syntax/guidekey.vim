if exists('b:current_syntax') && b:current_syntax ==# 'guidekey'
    finish
endif
let b:current_syntax = 'guidekey'

exe 'syntax match GuidekeySeperator "' . g:guidekey_seperator . '"'
highlight link GuidekeySeperator Comment
