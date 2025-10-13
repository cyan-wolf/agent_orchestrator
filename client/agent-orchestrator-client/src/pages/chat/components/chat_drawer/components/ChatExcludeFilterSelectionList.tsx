import * as React from 'react';
import OutlinedInput from '@mui/material/OutlinedInput';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, { type SelectChangeEvent } from '@mui/material/Select';

import { type MessageFilter } from '../../messages/message';
import { useChatContext } from '../../../Chat';

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

type FilterNameMap = {
    [name: string]: MessageFilter,
};

const filterNames: FilterNameMap = {
  'Tool Messages': 'tool',
  'Images': 'image',
  'AI Messages': 'ai_message',
  'Human Messages': 'human_message',
};

export default function ChatExcludeFilterSelectionList() {
  const [messageFilters, setMessageFilter] = React.useState<MessageFilter[]>([]);
  
  const { setExcludeFilters } = useChatContext()!;

  const handleChange = (event: SelectChangeEvent<typeof messageFilters>) => {
    const { target: { value } } = event;

    // On autofill we get a stringified value.
    const filterList: MessageFilter[] = (typeof value === 'string' ? value.split(',') : value) as MessageFilter[];

    setMessageFilter(filterList);
    setExcludeFilters(filterList);
  };

  return (
    <div>
      <FormControl sx={{ m: 1, width: 200 }}>
        <InputLabel id="exlcude-filters-label">Exclude Filters</InputLabel>
        <Select
          labelId="exlcude-filters-label"
          id="exclude-filters-select"
          multiple
          value={messageFilters}
          onChange={handleChange}
          input={<OutlinedInput label="Exclude Filters" />}
          MenuProps={MenuProps}
        >
          {Object.keys(filterNames).map((name) => (
            <MenuItem
              key={name}
              value={filterNames[name]}
            >
              {name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </div>
  );
}
