import { WireType } from "@protobuf-ts/runtime";
import { UnknownFieldHandler } from "@protobuf-ts/runtime";
import { reflectionMergePartial } from "@protobuf-ts/runtime";
import { MessageType } from "@protobuf-ts/runtime";
// @generated message type with reflection information, may provide speed optimized methods
class ContactFormConfig$Type extends MessageType {
    constructor() {
        super("website_content.v1.ContactFormConfig", [
            { no: 1, name: "form_action_uri", kind: "scalar", T: 9 /*ScalarType.STRING*/ },
            { no: 2, name: "success_message_key", kind: "scalar", T: 9 /*ScalarType.STRING*/ },
            { no: 3, name: "error_message_key", kind: "scalar", T: 9 /*ScalarType.STRING*/ }
        ]);
    }
    create(value) {
        const message = globalThis.Object.create((this.messagePrototype));
        message.formActionUri = "";
        message.successMessageKey = "";
        message.errorMessageKey = "";
        if (value !== undefined)
            reflectionMergePartial(this, message, value);
        return message;
    }
    internalBinaryRead(reader, length, options, target) {
        let message = target ?? this.create(), end = reader.pos + length;
        while (reader.pos < end) {
            let [fieldNo, wireType] = reader.tag();
            switch (fieldNo) {
                case /* string form_action_uri */ 1:
                    message.formActionUri = reader.string();
                    break;
                case /* string success_message_key */ 2:
                    message.successMessageKey = reader.string();
                    break;
                case /* string error_message_key */ 3:
                    message.errorMessageKey = reader.string();
                    break;
                default:
                    let u = options.readUnknownField;
                    if (u === "throw")
                        throw new globalThis.Error(`Unknown field ${fieldNo} (wire type ${wireType}) for ${this.typeName}`);
                    let d = reader.skip(wireType);
                    if (u !== false)
                        (u === true ? UnknownFieldHandler.onRead : u)(this.typeName, message, fieldNo, wireType, d);
            }
        }
        return message;
    }
    internalBinaryWrite(message, writer, options) {
        /* string form_action_uri = 1; */
        if (message.formActionUri !== "")
            writer.tag(1, WireType.LengthDelimited).string(message.formActionUri);
        /* string success_message_key = 2; */
        if (message.successMessageKey !== "")
            writer.tag(2, WireType.LengthDelimited).string(message.successMessageKey);
        /* string error_message_key = 3; */
        if (message.errorMessageKey !== "")
            writer.tag(3, WireType.LengthDelimited).string(message.errorMessageKey);
        let u = options.writeUnknownFields;
        if (u !== false)
            (u == true ? UnknownFieldHandler.onWrite : u)(this.typeName, message, writer);
        return writer;
    }
}
/**
 * @generated MessageType for protobuf message website_content.v1.ContactFormConfig
 */
export const ContactFormConfig = new ContactFormConfig$Type();
//# sourceMappingURL=contact_form_config.js.map