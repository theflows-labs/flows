import React from 'react';
import AceEditor from 'react-ace';

// Import ace modes and themes
import 'ace-builds/src-noconflict/mode-json';
import 'ace-builds/src-noconflict/mode-python';
import 'ace-builds/src-noconflict/theme-github';

export const CodeEditor = ({ 
  value, 
  onChange, 
  language = 'json',
  readOnly = false,
  height = '300px'
}) => {
  return (
    <AceEditor
      mode={language}
      theme="github"
      value={value}
      onChange={onChange}
      name="code-editor"
      editorProps={{ $blockScrolling: true }}
      setOptions={{
        useWorker: false,
        showLineNumbers: true,
        tabSize: 2,
      }}
      width="100%"
      height={height}
      readOnly={readOnly}
    />
  );
};

export default CodeEditor; 