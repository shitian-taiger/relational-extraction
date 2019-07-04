import React from 'react';
import './App.css';
import Predictor from './Predictor';


function App() {
  return (
    <div className="App">
      <div>
        <Predictor/>
      </div>
    </div>
  );
}

export default App;


class Span extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      text: props["text"]
    };
  }

  render() {
    return (
        <span>{this.state.text}</span>
    );
  }
}

