import React from 'react';
import { Button, Table } from 'semantic-ui-react';
import equal from 'fast-deep-equal';

class Results extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      oieResults: [],
      dpResults: [],
      nerOieResults: [],
      // Bitwise validity for user input
      validity: {oie: [], dp: [], nerOie: []}
    };
  }

  // Updating of Prediction Results: Set result array and instantiate validity index
  componentDidUpdate(prevProps, prevState, snapshot) {
    // Required since setState results in inf loop within componentDidUpdate
    if (!equal(this.props.results, prevProps.results)) {
      this.updatePredictionResults();
    }
  }
  updatePredictionResults() {
    let results = this.props.results;
    this.setState({
      oieResults: results.oie_prediction,
      dpResults: results.dp_prediction,
      nerOieResults: results.ner_oie_prediction,
      validity: {
        oie: results.oie_prediction.map(x => 0),
        dp: results.dp_prediction.map(x => 0),
        nerOie: results.ner_oie_prediction.map(x => 0)
      }
    });
  }

  // Process each prediction type (Array of tuples) into ResultLine(TableRow)
  getResArray(predictionType, arr) {
    let resLines = [];
    for (let i = 0; i < arr.length; i++) {
      let line = arr[i];
      resLines.push(<ResultLine
                    pType={predictionType}
                    key={i} // Each child in list requires unique key, not accessible in props
                    index={i}
                    text={line}
                    validateInstance={this.instanceValidation}/>);
    }
    return resLines;
  }

  /** To be called by ResultLine child class, result should contain:
      pType : Prediction Type
      index : Index of instance within prediction type
      validity : Whether instance is valid
     */
  instanceValidation = (result) => {
    if (result.pType === "OIE") {
      this.state.validity.oie[result.index] = (result.validity) ? 1 : 0;
    } else if (result.pType === "DP") {
      this.state.validity.dp[result.index] = (result.validity) ? 1 : 0;
    } else if (result.pType === "NER-OIE") {
      this.state.validity.nerOie[result.index] = (result.validity) ? 1 : 0;
    } else {
      console.log("Setting validity of invalid prediction type");
      throw("Invalid");
    }
  }

  // Pass validations to parent Base
  confirmValidations() {
    if (this.state.oieResults.length == 0 &&
        this.state.nerOieResults.length == 0 &&
        this.state.dpResults.length == 0) {
      alert("Please process a valid sentence");
      }
    this.props.onValidated(this.state.validity);
  }


  render() {
    let oieResLines = this.getResArray("OIE", this.state.oieResults);
    let dPLines = this.getResArray("DP", this.state.dpResults);
    let oieNerResLines = this.getResArray("NER-OIE", this.state.nerOieResults);
    return (
      <div className="Results">
        <div className="Results-Header"> Predicted Results </div>
        <div className="Results-Subheader"> OIE Results </div>
        <Table className="Results-Table">
          <Table.Body>
            {oieResLines}
          </Table.Body>
        </Table>

        <div className="Results-Subheader"> NER-OIE Results </div>
        <Table className="Results-Table">
          <Table.Body>
            {oieNerResLines}
          </Table.Body>
        </Table>

        <div className="Results-Subheader"> DP Results </div>
        <Table className="Results-Table">
          <Table.Body>
            {dPLines}
          </Table.Body>
        </Table>
        <Button onClick={() => this.confirmValidations()}>
          Confirm Validations
        </Button>
      </div>
    );
  }
}


class ResultLine extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      predictionType: props.pType,
      index: props.index,
      arg1: props.text[0],
      rel: props.text[1],
      arg2: props.text[2],
      valid: false,
      buttonText: "Validate",
    };
  }

  componentWillReceiveProps(nextProps) {
    this.updateArguments(nextProps);
  }

  // Indicates new sentence has been predicted
  updateArguments(res) {
    this.setState({
      arg1: res.text[0],
      rel: res.text[1],
      arg2: res.text[2],
      valid: false,
      buttonText: "Validate",
    });
  }

  // Handle the setting of validity here, also pass validity to parent
  setValidity() {
    let newValidity = this.state.valid ? false : true
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

export default Results;
