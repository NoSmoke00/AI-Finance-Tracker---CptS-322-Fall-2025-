// Temporary shim to satisfy editor/tsserver when JSX types are not resolved
declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}


