import React, {Component} from "react";
import PropTypes from "prop-types";

class Form extends Component {
    static propTypes = {
        endpoint: PropTypes.string.isRequired
    };
    state = {
        url: "",
    };
    handleChange = e => {
        this.setState({[e.target.name]: e.target.value});
    };
    handleSubmit = e => {
        e.preventDefault();
        const {url} = this.state;
        const repository = {url};
        const conf = {
            method: "post",
            body: JSON.stringify(repository),
            headers: new Headers({"Content-Type": "application/json"})
        };
        fetch(this.props.endpoint, conf).then(response => console.log(response));
    };

    render() {
        const {url} = this.state;
        return (
            <div className="column">
                <form onSubmit={this.handleSubmit}>
                    <div className="field">
                        <label className="label">Name</label>
                        <div className="control">
                            <input
                                className="input"
                                type="text"
                                name="url"
                                onChange={this.handleChange}
                                value={url}
                                required
                            />
                        </div>
                    </div>
                    <div className="control">
                        <button type="submit" className="button is-info">
                            Send message
                        </button>
                    </div>
                </form>
            </div>
        );
    }
}

export default Form;