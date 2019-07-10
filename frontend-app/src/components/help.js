import React from 'react';
import { Modal, Button, Header } from 'semantic-ui-react';


class HelpModal extends React.Component {

  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    return (
      <Modal floated="right" trigger={<Button> ? Help</Button>}>
        <Modal.Header>Relational Extraction FAQ</Modal.Header>
        <Modal.Content>
          <Header>What constitutes a Named Entity?</Header>
          <p></p>
          <Header>What represents a Relation?</Header>
          <p></p>
        </Modal.Content>
      </Modal>
    )
  }
}

export default HelpModal;

