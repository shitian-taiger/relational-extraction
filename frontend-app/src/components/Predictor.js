import React from 'react';
import { Message, Button, Input, Popup, Icon } from 'semantic-ui-react';

// let IP = "http://192.168.86.101:8000";
// let IP = "http://127.0.0.1:8000";
let IP = "http://192.168.86.248:8000";

function submitter(url, sentenceToPredict) {
  return fetch(url, {
    method: 'POST',
    body: JSON.stringify({
      sentence: sentenceToPredict,
    }),
  })
    .then((response) => response.json());
}

class Predictor extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      ARGSELECTINFO: "Highlight text and set as desired argument, `Add Relation` row below will be updated correspondinly (Note this only works for text within the current box)",
      sentence: "",
      selectedText: ""
    };
    this.textHighlightHandler = this.textHighlightHandler.bind(this);
    this.sentenceDisplay = React.createRef();
  }

  // Adding of mouse up event listener for selection of highlighted text
  componentDidMount() {
    window.addEventListener('mouseup', this.textHighlightHandler);
  }
  textHighlightHandler(event) {
    let sentenceNode = this.sentenceDisplay.current;
    let selectedText = window.getSelection().toString();
    if (sentenceNode.contains(event.target) && !(selectedText === "")) {
      this.setState({
        selectedText: selectedText
      });
    }
  }
  componentWillUnmount() {
    window.removeEventListener('mouseup', this.textHighlightHandler);
  }

  setHighlightedText(type) {
    this.props.onSetHighlighted(type, this.state.selectedText.trim());
  }

  render() {
    return (
      <div className="Predictor">
        <div className="Predictor-Header"> Open Relational Extraction </div>
        <SentenceInput onResultReceived={this.resultReceived}/>
        <Message style={{marginLeft: "30px", marginRight: "30px"}}>
          <Message.Header>Sentence</Message.Header>
          <Button size="mini" compact onClick={() => this.setHighlightedText("entity1")}>Entity 1</Button>
          <Button size="mini" compact onClick={() => this.setHighlightedText("relation")}>Relation</Button>
          <Button size="mini" compact onClick={() => this.setHighlightedText("entity2")}>Entity 2</Button>
          <Popup content={this.state.ARGSELECTINFO} trigger={<Icon name='info circle'/>} />
          <p ref={this.sentenceDisplay}>{this.state.sentence}</p>
        </Message>
      </div>
    );
  };

  resultReceived = (sentence, result) => {
    this.setState({
      sentence: sentence
    });
    this.props.onPredictionResult(sentence, result);
  }
}

class SentenceInput extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      sentence: "",
      oie_predict_url: IP + "/predict/all",
      oie_results: [],
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleKeyPress = this.handleKeyPress.bind(this);
  }

  handleChange(event) {
    let sentence = event.target.value.replace(/"/g, "'");
    this.setState({sentence: sentence});
  }

  // Allow `Enter` keypress to simulate button clicking
  handleKeyPress(target) {
    if(target.charCode === 13) { // `Enter` keycode
      submitter(this.state.oie_predict_url, this.state.sentence)
        .then((res) => this.props.onResultReceived(this.state.sentence, res))
        .catch((err) => alert("Server Error"));
    }
  }
  handleSubmit(event) {
    event.preventDefault();
    submitter(this.state.oie_predict_url, this.state.sentence)
      .then((res) => this.props.onResultReceived(this.state.sentence, res))
      .catch((err) => alert("Server Error"));
  }

  getNextSentence = (event) => {
    event.preventDefault();
    fetch(IP + "/get_sentence", {
      method: 'GET',
    })
      .then((response) => response.json())
      .then((responseJson) => {
        this.setState({
          sentence: responseJson.sentence
        });
      });
  }

  skipSentence = (event) => {
    fetch(IP + "/skip_sentence", {
      method: 'POST',
      body: JSON.stringify({
        sentence: this.state.sentence
      }),
    })
      .then((response) => response.json())
      .then((responseJson) => {
        this.setState({
          sentence: "" // Reset sentence since we marked it as skip
        });
        console.log(responseJson);
      });
  }

  render() {
    return (
      <div className="SentenceInput">
        <span className="SentenceInput-Label">
          Sentence Input:
        </span>
        <Input className="SentenceInput-Text"
               focus
               onKeyPress={this.handleKeyPress}
               placeholder="Enter a sentence"
               value={this.state.sentence}
               onChange={this.handleChange} />
        <Button style={{margin: "10px"}} onClick={this.handleSubmit} >
          Predict
        </Button>

        <Button style={{margin: "5px"}} onClick={this.skipSentence}>
        Skip Sentence
        </Button>

        <div>
          <Button onClick={this.getNextSentence}> Get Random Unprocessed Sentence </Button>
        </div>
      </div>
    );
  }
}


export default Predictor;
