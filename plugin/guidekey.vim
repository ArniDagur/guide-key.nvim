" vim: et:ts=4:sts=4:sw=4:fdm=marker
if exists('g:loaded_guidekey')
    finish
endif
let g:loaded_guidekey = 1

if !exists('g:guidekey_starting_data_dict')
    let g:guidekey_starting_data_dict = {}
endif

if !exists('g:guidekey_position')
    let g:guidekey_position = 'botright'
endif

if !exists('g:guidekey_vertical')
    let g:guidekey_vertical = 0
endif

if !exists('g:guidekey_statusline')
    let g:guidekey_statusline = "Guide Key"
endif

if !exists('g:guidekey_desc_dict')
    let g:guidekey_desc_dict = {}
endif

if !exists('g:guidekey_do_not_bind_keys')
    let g:guidekey_do_not_bind_keys = 0
endif

if !exists('g:guidekey_grid_seperator')
    let g:guidekey_grid_seperator = ' '
endif

if !exists('g:guidekey_column_margins')
    let g:guidekey_column_margins = [' ']
endif

if !exists('g:guidekey_grid_margins')
    let g:guidekey_grid_margins = [' ']
endif

if !exists('g:guidekey_prefix_desc_dict')
    let g:guidekey_prefix_desc_dict = {}
endif

if !exists('g:guidekey_seperator')
    let g:guidekey_seperator = ' -> '
endif

if !exists('g:guidekey_exit_on_esc')
    let g:guidekey_exit_on_esc = 1
endif
