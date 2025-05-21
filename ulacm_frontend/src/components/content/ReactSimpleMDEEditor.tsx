// File: ULACM2/ulacm_frontend/src/components/content/ReactSimpleMDEEditor.tsx
// Purpose: React-SimpleMDE (EasyMDE) based Markdown editor component.
// Changes:
// - Renamed 'initialContent' prop to 'value' for standard controlled component pattern.
// - Removed useEffect that manually set editor value on prop change; rely on SimpleMdeReact's 'value' prop.
// - Simplified getMdeInstance callback.
// - Ensured editable state is correctly applied.

import React, { useMemo, useCallback, useEffect, useRef } from 'react';
import SimpleMDE, { Options } from 'easymde';
import { SimpleMdeReact } from 'react-simplemde-editor';
import 'easymde/dist/easymde.min.css'; // Import EasyMDE's CSS

interface ReactSimpleMDEEditorProps {
  value: string; // Changed from initialContent
  onChange: (markdownContent: string) => void;
  editable?: boolean;
  placeholder?: string;
  debounceTime?: number;
}

const ReactSimpleMDEEditor: React.FC<ReactSimpleMDEEditorProps> = ({
  value, // Prop for the current editor content
  onChange,
  editable = true,
  placeholder = 'Start writing your content here...',
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  debounceTime = 500, // Debounce logic is handled by the parent or could be added here if needed
}) => {
  const mdeInstanceRef = useRef<SimpleMDE | null>(null);
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);


  // Memoize options to prevent re-creating the editor unnecessarily
  const editorOptions: Options = useMemo(() => {
    return {
      autofocus: false,
      spellChecker: false,
      placeholder: placeholder,
      status: false,
      toolbar: [
        'bold', 'italic', 'strikethrough', '|',
        'heading-1', 'heading-2', 'heading-3', '|',
        'quote', 'unordered-list', 'ordered-list', '|',
        'link', 'image', 'table', 'horizontal-rule', '|',
        'preview', 'side-by-side', 'fullscreen', '|',
        'guide'
      ],
      minHeight: '300px',
      // Ensure CodeMirror handles line breaks correctly for display
      // This is important for how Markdown newlines are treated visually in the editor input area
      inputStyle: 'contenteditable', // or 'textarea' - 'contenteditable' is default for EasyMDE
      // lineWrapping: true, // Default for CodeMirror in EasyMDE
    };
  }, [placeholder]);

  // Debounced onChange handler
  const handleEditorChange = useCallback(
    (currentValue: string) => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
      debounceTimeoutRef.current = setTimeout(() => {
        onChange(currentValue);
      }, debounceTime);
    },
    [onChange, debounceTime]
  );

  // Effect to update read-only state of CodeMirror instance
  useEffect(() => {
    if (mdeInstanceRef.current?.codemirror) {
      mdeInstanceRef.current.codemirror.setOption('readOnly', !editable);
    }
  }, [editable, mdeInstanceRef.current]);


  // Callback to get the SimpleMDE instance
  const getMdeInstance = useCallback((instance: SimpleMDE) => {
    mdeInstanceRef.current = instance;
    // Set initial read-only state when instance is available
    if (instance?.codemirror) {
        instance.codemirror.setOption('readOnly', !editable);
    }
  }, [editable]);

  // Cleanup debounce timer on unmount
  useEffect(() => {
    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div className={`ulacm-simplemde-editor-wrapper ${!editable ? 'readonly-editor-wrapper' : ''} rounded-lg border border-ulacm-gray-300 shadow-sm h-full flex flex-col`}>
      <SimpleMdeReact
        id="react-simplemde-editor" // Static ID for the component
        value={value} // Controlled component: value is driven by parent state
        onChange={handleEditorChange} // Updates parent state
        options={editorOptions}
        getMdeInstance={getMdeInstance}
      />
    </div>
  );
};

export default ReactSimpleMDEEditor;
