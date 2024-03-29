import React from 'react';
import { Button, Table } from 'semantic-ui-react';

export class ResultLine extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      predictionType: props.pType,
      index: props.index,
      arg1: props.text[0],
      rel: props.text[1],
      arg2: props.text[2],
      buttonText: "Validate"
    };
  }

  // This is called on creation of component, set for case USER where buttonText is Delete
  componentDidMount() {
    if (this.state.predictionType === "USER") {
      this.setState({
        valid: true,
        buttonText: "Delete"
      });
    }
  }

  // Updating new props, presumably only for updating validity
  componentWillReceiveProps(nextProps) {
    this.updateArguments(nextProps);
  }

  // Indicates new sentence has been predicted
  updateArguments(res) {
    this.setState({
      arg1: res.text[0],
      rel: res.text[1],
      arg2: res.text[2],
      valid: res.validity,
      buttonText: (res.validity) ? "Discard" : "Validate",
    });
  }

  // Handle the setting of validity here, also pass validity to parent
  setValidity() {
    let newValidity = this.state.valid ? false : true;
    let bText = (newValidity) ? "Discard" : "Validate";
    this.setState({
      valid: newValidity,
      buttonText: bText
    });
    // Pass instance validity to parent
    this.props.validateInstance({
      pType: this.state.predictionType,
      index: this.state.index,
      validity: newValidity
    });
  }

  render() {
    return (
      <Table.Row className="ResultLine">
        <Table.Cell>
          <Span valid={this.state.valid} text={this.state.arg1}/>
          <Span valid={this.state.valid} text={this.state.rel}/>
          <Span valid={this.state.valid} text={this.state.arg2}/>
        </Table.Cell>
        <Table.Cell textAlign='right'>
          <Button onClick={() => this.setValidity()}>
            {this.state.buttonText}
          </Button>
        </Table.Cell>
      </Table.Row>
    );
  }
}

class Span extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      text: props["text"],
    };
  }

  componentDidMount() {
    this.updateStyle(false);
  }

  componentWillReceiveProps(nextProps) {
    this.updateStyle(nextProps.valid);
    this.setState({
      text: nextProps["text"]
    });
  }

  // Style text differently based on validity
  updateStyle(valid) {
    if (valid) {
      this.setState({decoration: {
        color: "green",
        fontWeight: "bold",
        }
      });
    } else {
      this.setState({decoration: {
        textDecorationLine: "line-through",
        textDecorationStyle: "solid",
        }
      });
    }
  };

  render() {
    return (
      <span style={this.state.decoration} className="Text">
        {this.state.text}
      </span>
    );
  }
}

export default ResultLine;
